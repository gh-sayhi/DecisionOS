from __future__ import annotations

from datetime import datetime
from hashlib import sha1
import re
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from backend.services.storage import REPORT_DIR, ensure_report_dir


DecisionPack = Literal["Product", "Startup", "Marketing", "Content", "Hiring", "Investment", "Custom"]
DecisionLanguage = Literal["en", "zh"]
ExportFormat = Literal["pdf", "markdown"]


class DecisionRequest(BaseModel):
    title: str = Field(min_length=2)
    pack: DecisionPack
    language: DecisionLanguage = "en"
    context: str = Field(min_length=8)
    objective: str = Field(min_length=4)
    options: list[str] = Field(default_factory=list)
    constraints: str = ""
    budget: float = 0
    timeline: str = ""
    stakeholders: str = ""
    success_metrics: str = ""
    known_risks: str = ""


class FollowUpQuestion(BaseModel):
    id: str
    question: str
    context: str
    type: Literal["text", "textarea", "select", "multiselect"]
    options: list[str] | None = None
    answer: str | None = None


class FollowUpSession(BaseModel):
    decisionId: str
    questions: list[FollowUpQuestion]
    status: Literal["pending", "answering", "completed"]


class FollowUpRequest(BaseModel):
    pack: DecisionPack
    formData: dict[str, str | int | float | list[str] | None] = Field(default_factory=dict)


class FollowUpAnswer(BaseModel):
    id: str
    answer: str


class SubmitFollowUpAnswersRequest(BaseModel):
    decisionId: str
    answers: list[FollowUpAnswer]


class SubmitFollowUpAnswersResponse(BaseModel):
    decisionId: str
    combined_context: str
    status: Literal["completed"]


class RiskItem(BaseModel):
    risk: str
    likelihood: str
    impact: str
    mitigation: str


class TimelineItem(BaseModel):
    phase: str
    window: str
    output: str


class ReasoningStep(BaseModel):
    label: str
    focus: str
    signal: str
    status: str


class ActionItem(BaseModel):
    day: str
    task: str
    owner: str
    duration: str
    priority: str


class ScoringDimension(BaseModel):
    key: str
    label: str
    weight: float
    score: int
    reason: str


class ScoringSummary(BaseModel):
    pack: DecisionPack
    framework: str
    prompt: str
    extracted_signals: list[str]
    dimensions: list[ScoringDimension]
    total_score: int
    recommendation: str


class FeedbackChange(BaseModel):
    section: str
    before: str
    after: str
    reason: str


class BusinessCase(BaseModel):
    id: str
    title: str
    company: str
    year: int
    scenario: str
    pack: DecisionPack
    tags: list[str]
    budget: float
    timeline: str
    decision: str
    outcome: str
    lesson: str
    source: str | None = None


class MatchedBusinessCase(BusinessCase):
    similarity: int


class DecisionFeedbackRequest(BaseModel):
    decisionId: str
    feedback: str = Field(min_length=4)


class DecisionReport(BaseModel):
    report_id: str
    created_at: str
    pack: DecisionPack
    executive_summary: str
    decision_verdict: str
    core_value: list[str]
    benchmark: list[str]
    risk_matrix: list[RiskItem]
    execution_plan: list[str]
    budget: list[str]
    timeline: list[TimelineItem]
    next_actions: list[str]
    action_items: list[ActionItem]
    scoring_summary: ScoringSummary
    reference_cases: list[MatchedBusinessCase]
    reasoning_timeline: list[ReasoningStep]


class DecisionFeedbackResponse(BaseModel):
    changes: list[FeedbackChange]
    updatedReport: DecisionReport


router = APIRouter(prefix="/api/decision", tags=["decision-os"])


FOLLOWUP_TEMPLATES: dict[str, list[FollowUpQuestion]] = {
    "Product": [
        FollowUpQuestion(id="target_user", question="Who is the exact user segment this decision serves first?", context="Clarifies adoption risk and product scope.", type="textarea"),
        FollowUpQuestion(id="user_pain", question="What pain is urgent enough that users would change behavior now?", context="Separates real demand from nice-to-have features.", type="textarea"),
        FollowUpQuestion(id="mvp_boundary", question="What must be inside the first version, and what must stay out?", context="Prevents scope expansion before evidence exists.", type="textarea"),
        FollowUpQuestion(id="success_signal", question="Which one metric proves the product decision is working?", context="Creates a decision gate for launch or revision.", type="text"),
    ],
    "Startup": [
        FollowUpQuestion(id="wedge", question="What is the smallest market wedge where you can win first?", context="Checks whether the startup decision has a focused entry point.", type="textarea"),
        FollowUpQuestion(id="unfair_advantage", question="What advantage do you have that competitors cannot easily copy?", context="Supports founder-market and defensibility assessment.", type="textarea"),
        FollowUpQuestion(id="runway_gate", question="What proof must exist before spending the next major budget tranche?", context="Aligns execution with runway and financing risk.", type="textarea"),
    ],
    "Marketing": [
        FollowUpQuestion(id="segment", question="Which segment should receive the first marketing push?", context="Avoids spreading budget across weak audiences.", type="text"),
        FollowUpQuestion(id="message", question="What message would make that segment act now?", context="Checks message-market fit.", type="textarea"),
        FollowUpQuestion(id="channel", question="Which channel has the strongest evidence of conversion?", context="Grounds the growth decision in measurable behavior.", type="select", options=["Owned", "Paid", "Partner", "Sales-led", "Community", "Other"]),
        FollowUpQuestion(id="pipeline_goal", question="What pipeline or revenue result must this campaign produce?", context="Connects the marketing decision to business impact.", type="text"),
    ],
    "Content": [
        FollowUpQuestion(id="audience", question="Who is the most valuable audience for this content decision?", context="Clarifies audience intent and distribution fit.", type="textarea"),
        FollowUpQuestion(id="format", question="Which format gives the best balance of quality, speed, and cost?", context="Keeps the content decision operational rather than abstract.", type="select", options=["Article", "Video", "Newsletter", "Podcast", "Short-form", "Mixed"]),
        FollowUpQuestion(id="cadence", question="What cadence can the team sustain without quality drop?", context="Checks production feasibility.", type="text"),
    ],
    "Hiring": [
        FollowUpQuestion(id="capability_gap", question="What capability gap is blocking the business outcome?", context="Determines whether hiring is the right solution.", type="textarea"),
        FollowUpQuestion(id="role_level", question="What seniority level is truly required?", context="Prevents over-hiring or under-scoping the role.", type="select", options=["IC", "Senior IC", "Manager", "Director", "Fractional", "Contractor"]),
        FollowUpQuestion(id="ramp_expectation", question="What must this person deliver in the first 90 days?", context="Creates a concrete hiring success gate.", type="textarea"),
        FollowUpQuestion(id="alternative", question="Can the gap be solved by redesigning work, contracting, or promoting internally?", context="Compares hiring against lower-risk alternatives.", type="textarea"),
    ],
    "Investment": [
        FollowUpQuestion(id="investment_thesis", question="What is the investment thesis in one sentence?", context="Separates conviction from narrative.", type="textarea"),
        FollowUpQuestion(id="downside", question="What is the most credible downside case?", context="Clarifies risk-adjusted return.", type="textarea"),
        FollowUpQuestion(id="liquidity", question="How would this decision affect liquidity or optionality?", context="Checks capital flexibility.", type="textarea"),
        FollowUpQuestion(id="exit_gate", question="What condition would make you exit or stop funding this path?", context="Defines loss control before commitment.", type="textarea"),
    ],
    "Custom": [
        FollowUpQuestion(id="decision_owner", question="Who owns the final decision?", context="Avoids unclear accountability.", type="text"),
        FollowUpQuestion(id="irreversible_part", question="Which part of the decision is hardest to reverse?", context="Focuses the risk review.", type="textarea"),
        FollowUpQuestion(id="proof_needed", question="What evidence would change the recommendation?", context="Creates a useful validation gate.", type="textarea"),
    ],
}

FOLLOWUP_TEMPLATES_ZH: dict[str, list[FollowUpQuestion]] = {
    "Product": [
        FollowUpQuestion(id="target_user", question="这个决策首先要服务哪类用户？", context="明确采用风险和产品范围。", type="textarea"),
        FollowUpQuestion(id="user_pain", question="用户的什么痛点迫切到足以让他们改变现有行为？", context="区分真实需求与锦上添花的功能。", type="textarea"),
        FollowUpQuestion(id="mvp_boundary", question="哪些功能必须在第一版里面，哪些必须排除？", context="防止在有证据之前无限扩大范围。", type="textarea"),
        FollowUpQuestion(id="success_signal", question="哪一个指标可以证明这个产品决策是对的？", context="建立发布或调整的决策门禁。", type="text"),
    ],
    "Startup": [
        FollowUpQuestion(id="wedge", question="最小的市场切入点是什么？", context="检查 startup 决策是否有聚焦的突破口。", type="textarea"),
        FollowUpQuestion(id="unfair_advantage", question="你有什么竞争对手难以复制的优势？", context="支撑创始人-市场匹配和防御能力评估。", type="textarea"),
        FollowUpQuestion(id="runway_gate", question="在动用下一笔重大预算之前，必须证明什么？", context="对齐执行节奏与资金风险。", type="textarea"),
    ],
    "Marketing": [
        FollowUpQuestion(id="segment", question="第一次营销推广应该针对哪个细分市场？", context="避免将预算分散到弱势受众。", type="text"),
        FollowUpQuestion(id="message", question="什么信息能让这个细分市场立即行动？", context="检验信息-市场匹配度。", type="textarea"),
        FollowUpQuestion(id="channel", question="哪个渠道有最强的转化证据？", context="将增长决策建立在可衡量的行为上。", type="select", options=["自有", "付费", "合作", "销售驱动", "社区", "其他"]),
        FollowUpQuestion(id="pipeline_goal", question="这次推广必须产生多少管道或收入？", context="将营销决策与业务影响挂钩。", type="text"),
    ],
    "Content": [
        FollowUpQuestion(id="audience", question="这个内容决策最有价值的受众是谁？", context="明确受众意图和分发匹配度。", type="textarea"),
        FollowUpQuestion(id="format", question="哪种形式能在质量、速度和成本之间取得最佳平衡？", context="让内容决策保持可操作性而非抽象。", type="select", options=["文章", "视频", "通讯", "播客", "短视频", "混合"]),
        FollowUpQuestion(id="cadence", question="在不降低质量的前提下，团队能维持什么发布频率？", context="检查生产可行性。", type="text"),
    ],
    "Hiring": [
        FollowUpQuestion(id="capability_gap", question="什么能力缺口在阻碍业务成果？", context="确定招聘是否是正确的解决方案。", type="textarea"),
        FollowUpQuestion(id="role_level", question="真正需要什么职级的人？", context="防止过度招聘或低估岗位要求。", type="select", options=["个人贡献者", "高级IC", "经理", "总监", "兼职", "外包"]),
        FollowUpQuestion(id="ramp_expectation", question="这个人必须在入职 90 天内交付什么？", context="建立具体的招聘成功门禁。", type="textarea"),
        FollowUpQuestion(id="alternative", question="这个缺口能否通过重新分配工作、外包或内部晋升来解决？", context="比较招聘与低风险替代方案。", type="textarea"),
    ],
    "Investment": [
        FollowUpQuestion(id="investment_thesis", question="用一句话概括投资逻辑？", context="区分信念与叙事。", type="textarea"),
        FollowUpQuestion(id="downside", question="最可信的下行风险是什么？", context="明确风险调整后回报。", type="textarea"),
        FollowUpQuestion(id="liquidity", question="这个决策会如何影响流动性或选择权？", context="检查资本灵活性。", type="textarea"),
        FollowUpQuestion(id="exit_gate", question="什么情况下你会退出或停止对这个方向的投资？", context="在承诺投入前明确损失控制条件。", type="textarea"),
    ],
    "Custom": [
        FollowUpQuestion(id="decision_owner", question="谁来最终决策？", context="避免责任不清。", type="text"),
        FollowUpQuestion(id="irreversible_part", question="这个决策的哪部分最难逆转？", context="聚焦风险审查。", type="textarea"),
        FollowUpQuestion(id="proof_needed", question="什么证据会改变当前的推荐建议？", context="建立有用的验证门禁。", type="textarea"),
    ],
}

FOLLOWUP_SESSIONS: dict[str, dict[str, object]] = {}
REPORT_STORE: dict[str, DecisionReport] = {}

ACTION_LIST_PROMPT_INSTRUCTION = (
    "At the end of every decision report, output a concrete weekly action list. "
    "Each action item must include time, task, owner, duration, and priority."
)

FONT_NAME = "STHeiti-Light"
FONT_PATH = "/System/Library/Fonts/STHeiti Light.ttc"

try:
    pdfmetrics.getFont(FONT_NAME)
except KeyError:
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

PDF_STYLES = getSampleStyleSheet()
PDF_STYLES.add(ParagraphStyle(name="DecisionTitle", parent=PDF_STYLES["Title"], fontName=FONT_NAME, fontSize=20, leading=26, textColor=colors.HexColor("#111827"), spaceAfter=12))
PDF_STYLES.add(ParagraphStyle(name="DecisionHeading", parent=PDF_STYLES["Heading2"], fontName=FONT_NAME, fontSize=13, leading=18, textColor=colors.HexColor("#1f2937"), spaceBefore=10, spaceAfter=6))
PDF_STYLES.add(ParagraphStyle(name="DecisionBody", parent=PDF_STYLES["BodyText"], fontName=FONT_NAME, fontSize=10, leading=15, wordWrap="CJK"))

PACK_SCORING_MODELS: dict[str, dict[str, object]] = {
    "Product": {
        "framework": "RICE",
        "prompt": "Extract user reach, expected impact, evidence confidence, and execution effort. Score each dimension from 0-100, then calculate the weighted RICE decision score.",
        "dimensions": [
            ("reach", "Reach", 0.3),
            ("impact", "Impact", 0.3),
            ("confidence", "Confidence", 0.2),
            ("effort", "Effort", 0.2),
        ],
    },
    "Startup": {
        "framework": "Startup Entry Score",
        "prompt": "Extract market size, problem fit, team fit, timing, and funding readiness. Score each dimension from 0-100, then calculate the weighted startup decision score.",
        "dimensions": [
            ("market_size", "Market Size", 0.25),
            ("problem_fit", "Problem Fit", 0.25),
            ("team_fit", "Team Fit", 0.2),
            ("timing", "Timing", 0.15),
            ("funding", "Funding", 0.15),
        ],
    },
    "Marketing": {
        "framework": "Growth Allocation Score",
        "prompt": "Extract channel ROI, audience fit, brand awareness lift, and budget efficiency. Score each dimension from 0-100, then calculate the weighted marketing decision score.",
        "dimensions": [
            ("channel_roi", "Channel ROI", 0.35),
            ("audience_fit", "Audience Fit", 0.3),
            ("brand_awareness", "Brand Awareness", 0.15),
            ("budget_efficiency", "Budget Efficiency", 0.2),
        ],
    },
    "Content": {
        "framework": "Content Decision Score",
        "prompt": "Extract audience intent, format fit, distribution leverage, and production feasibility. Score each dimension from 0-100, then calculate the weighted content decision score.",
        "dimensions": [
            ("audience_intent", "Audience Intent", 0.3),
            ("format_fit", "Format Fit", 0.25),
            ("distribution", "Distribution", 0.25),
            ("production_feasibility", "Production Feasibility", 0.2),
        ],
    },
    "Hiring": {
        "framework": "Hiring Decision Score",
        "prompt": "Extract role urgency, budget fit, market salary pressure, and team capability gap. Score each dimension from 0-100, then calculate the weighted hiring decision score.",
        "dimensions": [
            ("urgency", "Urgency", 0.3),
            ("budget_fit", "Budget Fit", 0.25),
            ("market_salary", "Market Salary", 0.2),
            ("team_gap", "Team Gap", 0.25),
        ],
    },
    "Investment": {
        "framework": "Investment Committee Score",
        "prompt": "Extract risk-return profile, exit probability, market timing, and team quality. Score each dimension from 0-100, then calculate the weighted investment decision score.",
        "dimensions": [
            ("risk_return", "Risk Return", 0.35),
            ("exit_probability", "Exit Probability", 0.25),
            ("market_timing", "Market Timing", 0.2),
            ("team_quality", "Team Quality", 0.2),
        ],
    },
    "Custom": {
        "framework": "Strategic Decision Score",
        "prompt": "Extract strategic fit, evidence quality, reversibility, and execution readiness. Score each dimension from 0-100, then calculate the weighted custom decision score.",
        "dimensions": [
            ("strategic_fit", "Strategic Fit", 0.3),
            ("evidence_quality", "Evidence Quality", 0.25),
            ("reversibility", "Reversibility", 0.2),
            ("execution_readiness", "Execution Readiness", 0.25),
        ],
    },
}

DIMENSION_LABELS_ZH: dict[str, str] = {
    "reach": "覆盖范围",
    "impact": "影响程度",
    "confidence": "置信度",
    "effort": "执行成本",
    "market_size": "市场规模",
    "problem_fit": "问题匹配度",
    "team_fit": "团队适配度",
    "timing": "时机",
    "funding": "资金准备",
    "channel_roi": "渠道 ROI",
    "audience_fit": "受众匹配度",
    "brand_awareness": "品牌认知度",
    "budget_efficiency": "预算效率",
    "audience_intent": "受众意图",
    "format_fit": "形式适配度",
    "distribution": "分发能力",
    "production_feasibility": "生产可行性",
    "urgency": "紧急度",
    "budget_fit": "预算匹配度",
    "market_salary": "市场薪资",
    "team_gap": "团队缺口",
    "risk_return": "风险回报比",
    "exit_probability": "退出概率",
    "market_timing": "市场时机",
    "team_quality": "团队质量",
    "strategic_fit": "战略匹配度",
    "evidence_quality": "证据质量",
    "reversibility": "可逆性",
    "execution_readiness": "执行准备度",
}

CASE_TITLES_ZH: dict[str, str] = {
    "product-stripe-tax": "Stripe 税务模块上线",
    "product-notion-ai": "Notion AI 发布",
    "product-figma-collaboration": "Figma 协作功能扩展",
    "product-slack-pmf": "Slack 产品市场契合验证",
    "startup-airbnb-growth": "Airbnb 早期增长",
    "startup-dropbox-mvp": "Dropbox MVP 冷启动",
    "startup-canva-platform": "Canva 从工具到平台",
    "startup-uber-expansion": "Uber 城市扩张",
    "marketing-dsc-viral": "Dollar Shave Club 病毒营销",
    "marketing-duolingo-growth": "Duolingo 增长飞轮",
    "marketing-allbirds-dtc": "Allbirds DTC 品牌策略",
    "marketing-hubspot-inbound": "HubSpot 集客营销",
    "hiring-netflix-density": "Netflix 人才密度策略",
    "hiring-basecamp-small": "Basecamp 小团队哲学",
    "hiring-google-process": "Google 招聘流程",
    "hiring-github-remote": "GitHub 远程招聘",
    "investment-yc-framework": "YC 投资决策框架",
    "investment-sequoia-scouting": "Sequoia 赛道选择",
    "investment-a16z-enterprise": "a16z 企业投资策略",
    "investment-softbank-vision": "SoftBank 愿景基金",
    "content-red-bull": "Red Bull 内容营销",
    "content-netflix-original": "Netflix 原创内容策略",
    "content-morning-brew": "Morning Brew 通讯增长",
    "custom-amazon-prime": "Amazon Prime 会员策略",
    "custom-microsoft-cloud": "Microsoft 云转型",
    "custom-adobe-cc": "Adobe 订阅转型",
}

BUSINESS_CASES: list[BusinessCase] = [
    BusinessCase(id="product-stripe-tax", title="Stripe Tax module launch strategy", company="Stripe", year=2021, scenario="Expanded a payments platform into tax compliance.", pack="Product", tags=["platform", "compliance", "module", "enterprise", "launch"], budget=500000, timeline="12 months", decision="Ship a focused tax automation module.", outcome="Created a higher-value product surface beyond payments.", lesson="A strong product extension starts from a painful workflow adjacent to the core product."),
    BusinessCase(id="product-notion-ai", title="Notion AI launch", company="Notion", year=2023, scenario="Embedded AI workflows inside an existing workspace.", pack="Product", tags=["ai", "workspace", "productivity", "activation", "collaboration"], budget=300000, timeline="6 months", decision="Add AI as a native workflow layer.", outcome="Strengthened retention and monetization.", lesson="AI features work best when they reduce friction in an already frequent workflow."),
    BusinessCase(id="product-figma-collaboration", title="Figma collaboration expansion", company="Figma", year=2016, scenario="Made browser-native multiplayer design collaboration central.", pack="Product", tags=["collaboration", "browser", "design", "team", "workflow"], budget=250000, timeline="18 months", decision="Prioritize real-time collaboration.", outcome="Created a differentiated wedge against incumbents.", lesson="A product can win by changing the collaboration model."),
    BusinessCase(id="product-slack-pmf", title="Slack product-market fit validation", company="Slack", year=2013, scenario="Turned an internal tool into team collaboration software.", pack="Product", tags=["pmf", "team", "communication", "retention", "activation"], budget=200000, timeline="9 months", decision="Validate with teams with intense communication pain.", outcome="High retention and organic expansion became the signal.", lesson="Early PMF is visible through repeated team usage."),
    BusinessCase(id="startup-airbnb-growth", title="Airbnb early growth", company="Airbnb", year=2009, scenario="Built supply and trust in a lodging marketplace.", pack="Startup", tags=["marketplace", "growth", "trust", "supply", "wedge"], budget=80000, timeline="12 months", decision="Focus on dense city launches and listing quality.", outcome="Improved conversion and repeatable expansion.", lesson="Marketplace growth often starts with manual quality work."),
    BusinessCase(id="startup-dropbox-mvp", title="Dropbox MVP cold start", company="Dropbox", year=2007, scenario="Validated file sync demand before full product build.", pack="Startup", tags=["mvp", "cold-start", "video", "validation", "demand"], budget=50000, timeline="3 months", decision="Use a demo video to prove demand.", outcome="Waitlist demand validated the thesis.", lesson="Demand can be tested with a clear artifact before heavy build-out."),
    BusinessCase(id="startup-canva-platform", title="Canva from design tool to platform", company="Canva", year=2015, scenario="Expanded into templates, collaboration, and ecosystem.", pack="Startup", tags=["platform", "templates", "collaboration", "international", "growth"], budget=400000, timeline="24 months", decision="Broaden the wedge into a platform for non-designers.", outcome="Scaled into a horizontal creative operating system.", lesson="An underserved user can support platform strategy when workflows repeat."),
    BusinessCase(id="startup-uber-expansion", title="Uber market expansion", company="Uber", year=2011, scenario="Scaled a city-by-city transportation marketplace.", pack="Startup", tags=["marketplace", "city-launch", "operations", "supply", "timing"], budget=600000, timeline="18 months", decision="Repeat a local launch playbook.", outcome="Rapid expansion created category leadership.", lesson="Operational playbooks matter when expansion depends on local liquidity."),
    BusinessCase(id="marketing-dollar-shave-club", title="Dollar Shave Club viral launch", company="Dollar Shave Club", year=2012, scenario="Used a sharp launch video to create DTC demand.", pack="Marketing", tags=["viral", "dtc", "video", "subscription", "brand"], budget=4500, timeline="1 month", decision="Use humor and a direct value proposition.", outcome="Generated massive awareness and subscriptions.", lesson="A clear wedge and memorable creative can outperform large media spend."),
    BusinessCase(id="marketing-duolingo-flywheel", title="Duolingo growth flywheel", company="Duolingo", year=2020, scenario="Built social content and habit loops into growth.", pack="Marketing", tags=["growth", "social", "retention", "flywheel", "brand"], budget=120000, timeline="12 months", decision="Lean into distinctive social personality.", outcome="Expanded awareness while reinforcing daily engagement.", lesson="Marketing flywheels work when they reinforce product behavior."),
    BusinessCase(id="marketing-allbirds-dtc", title="Allbirds DTC brand strategy", company="Allbirds", year=2016, scenario="Built a DTC brand around simplicity and sustainability.", pack="Marketing", tags=["dtc", "brand", "sustainability", "positioning", "community"], budget=250000, timeline="9 months", decision="Anchor the brand around comfort and materials.", outcome="Created category differentiation and advocacy.", lesson="DTC brands need a simple reason to believe."),
    BusinessCase(id="marketing-hubspot-inbound", title="HubSpot inbound marketing category creation", company="HubSpot", year=2009, scenario="Turned educational content into B2B acquisition.", pack="Marketing", tags=["b2b", "content", "inbound", "pipeline", "category"], budget=150000, timeline="18 months", decision="Educate the market and own the inbound narrative.", outcome="Built repeatable organic demand and pipeline.", lesson="Category marketing compounds when content, product, and sales share language."),
    BusinessCase(id="hiring-netflix-density", title="Netflix talent density strategy", company="Netflix", year=2009, scenario="Prioritized high talent density and autonomy.", pack="Hiring", tags=["talent-density", "culture", "seniority", "performance", "team"], budget=1000000, timeline="24 months", decision="Hire and retain high-performing senior talent.", outcome="Created a culture optimized for judgment and speed.", lesson="Hiring quality can be a strategy when the model supports autonomy."),
    BusinessCase(id="hiring-basecamp-small-team", title="Basecamp small team philosophy", company="Basecamp", year=2010, scenario="Maintained a small senior team with constrained scope.", pack="Hiring", tags=["small-team", "scope", "remote", "senior", "efficiency"], budget=350000, timeline="12 months", decision="Avoid over-hiring and protect product focus.", outcome="Sustained profitability and calm operations.", lesson="Not hiring can be right when scope discipline is stronger leverage."),
    BusinessCase(id="hiring-google-process", title="Google structured hiring process", company="Google", year=2004, scenario="Built structured interviews and hiring committees.", pack="Hiring", tags=["process", "interview", "calibration", "scale", "quality"], budget=800000, timeline="18 months", decision="Standardize hiring signals for scale.", outcome="Improved consistency while scaling technical hiring.", lesson="Hiring systems need calibration when decision volume scales."),
    BusinessCase(id="hiring-github-remote", title="GitHub remote-first engineering hiring", company="GitHub", year=2014, scenario="Expanded engineering hiring beyond one geography.", pack="Hiring", tags=["remote", "engineering", "distributed", "talent", "process"], budget=450000, timeline="12 months", decision="Use remote work to access specialized talent.", outcome="Built distributed engineering capacity early.", lesson="Remote hiring works when documentation and ownership are explicit."),
    BusinessCase(id="investment-yc-framework", title="YC early-stage investment framework", company="Y Combinator", year=2005, scenario="Invested using founder quality, speed, and insight.", pack="Investment", tags=["early-stage", "founder", "speed", "market", "portfolio"], budget=125000, timeline="3 months", decision="Back teams with high learning velocity.", outcome="Created a repeatable early-stage portfolio model.", lesson="Founder learning speed can outweigh complete market proof."),
    BusinessCase(id="investment-sequoia-thesis", title="Sequoia sector selection logic", company="Sequoia Capital", year=2010, scenario="Used market maps and timing to concentrate conviction.", pack="Investment", tags=["thesis", "market", "category", "timing", "conviction"], budget=5000000, timeline="24 months", decision="Build conviction around large markets.", outcome="Supported concentrated bets in durable categories.", lesson="Investment quality improves when timing and company quality are evaluated together."),
    BusinessCase(id="investment-a16z-enterprise", title="a16z enterprise investment strategy", company="Andreessen Horowitz", year=2013, scenario="Backed enterprise software with GTM support.", pack="Investment", tags=["enterprise", "gtm", "software", "network", "scale"], budget=3000000, timeline="18 months", decision="Invest where enterprise adoption and founder-market fit compound.", outcome="Built a strong enterprise software portfolio thesis.", lesson="Capital plus GTM support can change the risk-return profile."),
    BusinessCase(id="investment-softbank-vision", title="SoftBank Vision Fund concentration lesson", company="SoftBank", year=2017, scenario="Deployed large checks into category leaders.", pack="Investment", tags=["growth", "concentration", "risk", "capital", "valuation"], budget=10000000, timeline="36 months", decision="Use capital scale to accelerate market leadership.", outcome="Mixed outcomes highlighted valuation and governance risk.", lesson="Large capital deployment raises the cost of wrong timing."),
    BusinessCase(id="content-red-bull-media", title="Red Bull media house strategy", company="Red Bull", year=2007, scenario="Built owned media around extreme sports and lifestyle.", pack="Content", tags=["owned-media", "brand", "video", "community", "distribution"], budget=1000000, timeline="24 months", decision="Invest in content as a brand-owned distribution asset.", outcome="Created durable brand association and reach.", lesson="Content compounds when the brand owns a cultural territory."),
    BusinessCase(id="content-netflix-originals", title="Netflix originals content bet", company="Netflix", year=2013, scenario="Moved from licensed catalog to original programming.", pack="Content", tags=["originals", "subscription", "retention", "data", "portfolio"], budget=100000000, timeline="24 months", decision="Commit to originals for differentiation and retention.", outcome="Strengthened subscription moat and global brand.", lesson="Original content is strategic when it improves retention and pricing power."),
    BusinessCase(id="content-morning-brew", title="Morning Brew newsletter growth", company="Morning Brew", year=2018, scenario="Scaled a daily business newsletter through referrals.", pack="Content", tags=["newsletter", "referral", "voice", "audience", "cadence"], budget=75000, timeline="12 months", decision="Use consistent voice and referral mechanics.", outcome="Built a highly engaged business audience.", lesson="Cadence and voice matter when content becomes a habit product."),
    BusinessCase(id="custom-amazon-prime", title="Amazon Prime strategic bundle", company="Amazon", year=2005, scenario="Bundled shipping benefits into membership.", pack="Custom", tags=["bundle", "membership", "retention", "commerce", "strategy"], budget=5000000, timeline="18 months", decision="Trade short-term shipping cost for long-term frequency.", outcome="Increased retention and ecosystem leverage.", lesson="A bundle works when one benefit changes customer behavior across the system."),
    BusinessCase(id="custom-microsoft-cloud", title="Microsoft cloud-first strategic shift", company="Microsoft", year=2014, scenario="Shifted priority from Windows-first to cloud-first.", pack="Custom", tags=["strategy", "cloud", "platform", "enterprise", "transformation"], budget=10000000, timeline="36 months", decision="Reorient resources and culture around Azure.", outcome="Repositioned the company for enterprise cloud growth.", lesson="Major strategy requires resource reallocation, not only messaging."),
    BusinessCase(id="custom-adobe-subscription", title="Adobe Creative Cloud subscription transition", company="Adobe", year=2012, scenario="Moved from perpetual licenses to subscription cloud.", pack="Custom", tags=["subscription", "pricing", "cloud", "transition", "retention"], budget=3000000, timeline="24 months", decision="Accept short-term disruption to build recurring revenue.", outcome="Created a stronger SaaS business model.", lesson="Business model transitions need clear migration paths and investor communication."),
]


PACK_LENS: dict[str, dict[str, str]] = {
    "Product": {
        "benchmark": "customer pain intensity, product differentiation, adoption friction, retention path",
        "value": "turn user demand into a prioritized product decision with measurable adoption signals",
    },
    "Startup": {
        "benchmark": "market timing, founder-market fit, capital efficiency, initial wedge",
        "value": "convert ambiguity into a staged venture decision with clear go/no-go gates",
    },
    "Marketing": {
        "benchmark": "segment clarity, message-market fit, channel leverage, conversion economics",
        "value": "choose the growth motion most likely to produce accountable pipeline",
    },
    "Content": {
        "benchmark": "audience intent, narrative angle, distribution fit, production leverage",
        "value": "shape a content initiative into a decision on audience, format, budget, and operating cadence",
    },
    "Hiring": {
        "benchmark": "role criticality, capability gap, ramp time, team leverage",
        "value": "decide whether to hire, wait, contract, or redesign the role",
    },
    "Investment": {
        "benchmark": "risk-adjusted return, downside exposure, liquidity, strategic fit",
        "value": "separate conviction from assumption before committing capital",
    },
    "Custom": {
        "benchmark": "strategic fit, opportunity cost, risk exposure, reversibility",
        "value": "structure a high-stakes decision into evidence, tradeoffs, and next actions",
    },
}

PACK_LENS_ZH: dict[str, dict[str, str]] = {
    "Product": {
        "benchmark": "用户痛点强度、产品差异化、采用阻力、留存路径",
        "value": "把用户需求转化为有优先级、可验证的产品决策",
    },
    "Startup": {
        "benchmark": "市场时机、创始团队匹配度、资本效率、初始切入点",
        "value": "把创业不确定性拆成带阶段门的进入决策",
    },
    "Marketing": {
        "benchmark": "人群清晰度、信息匹配度、渠道杠杆、转化经济性",
        "value": "选择最可能带来可归因业务管道的增长动作",
    },
    "Content": {
        "benchmark": "受众意图、叙事角度、分发匹配度、生产杠杆",
        "value": "把内容项目转化为关于受众、形式、预算和节奏的经营决策",
    },
    "Hiring": {
        "benchmark": "岗位关键性、能力缺口、上手周期、团队杠杆",
        "value": "判断应该招聘、暂缓、外包，还是重新设计岗位",
    },
    "Investment": {
        "benchmark": "风险调整回报、下行敞口、流动性、战略匹配度",
        "value": "在投入资金前区分真实信心和未经验证的假设",
    },
    "Custom": {
        "benchmark": "战略匹配、机会成本、风险敞口、可逆性",
        "value": "把重大开放问题结构化为证据、取舍和下一步动作",
    },
}


def _split_options(options: list[str]) -> list[str]:
    clean = [item.strip() for item in options if item.strip()]
    return clean or ["Proceed with a controlled pilot", "Pause and gather stronger evidence", "Redesign the option set"]


def _confidence(request: DecisionRequest) -> tuple[str, str]:
    evidence_score = sum(
        bool(value.strip())
        for value in [request.context, request.objective, request.constraints, request.stakeholders, request.success_metrics, request.known_risks]
    )
    if evidence_score >= 5 and request.budget > 0:
        return "Proceed with staged execution", "High"
    if evidence_score >= 4:
        return "Proceed with a validation gate", "Medium"
    return "Do not scale yet; run discovery first", "Low"


def _confidence_zh(request: DecisionRequest) -> tuple[str, str]:
    evidence_score = sum(
        bool(value.strip())
        for value in [request.context, request.objective, request.constraints, request.stakeholders, request.success_metrics, request.known_risks]
    )
    if evidence_score >= 5 and request.budget > 0:
        return "建议分阶段推进", "高"
    if evidence_score >= 4:
        return "建议先通过验证门再推进", "中"
    return "暂不放大投入，先补充调研和证据", "低"


def _clean_sentence(value: str) -> str:
    return value.strip().rstrip("。.!！?？")


def _bounded_score(value: float) -> int:
    return max(0, min(100, round(value)))


def _keyword_score(text: str, keywords: list[str], points: int = 7) -> int:
    lowered = text.lower()
    return min(28, sum(points for keyword in keywords if keyword.lower() in lowered))


def _extract_decision_signals(request: DecisionRequest, options: list[str]) -> list[str]:
    signals = [
        f"Pack-specific model: {PACK_SCORING_MODELS[request.pack]['framework']}",
        f"Options under review: {len(options)}",
    ]
    if request.budget > 0:
        signals.append(f"Budget available: {request.budget:,.0f}")
    if request.timeline:
        signals.append(f"Time horizon: {request.timeline}")
    if request.success_metrics:
        signals.append("Success metrics are defined")
    if request.known_risks:
        signals.append("Known risks are explicitly stated")
    if request.stakeholders:
        signals.append("Stakeholders are identified")
    if len(request.context) > 180:
        signals.append("Context includes detailed evidence")
    return signals


def _score_dimension(key: str, request: DecisionRequest, options: list[str]) -> tuple[int, str]:
    combined = " ".join(
        [
            request.title,
            request.context,
            request.objective,
            request.constraints,
            request.timeline,
            request.stakeholders,
            request.success_metrics,
            request.known_risks,
            " ".join(options),
        ]
    )
    evidence = 44
    evidence += min(18, len(request.context) / 35)
    evidence += 8 if request.success_metrics else 0
    evidence += 6 if request.stakeholders else 0
    evidence += 5 if len(options) >= 2 else 0
    evidence -= 8 if request.known_risks and not request.constraints else 0

    dimension_keywords = {
        "reach": ["enterprise", "segment", "users", "accounts", "teams", "market"],
        "impact": ["revenue", "activation", "retention", "conversion", "pipeline", "throughput"],
        "confidence": ["evidence", "pilot", "metrics", "validated", "proof", "data"],
        "effort": ["limited", "capacity", "weeks", "mvp", "small team", "resource"],
        "market_size": ["market", "category", "mid-market", "enterprise", "tam", "demand"],
        "problem_fit": ["pain", "urgent", "problem", "demand", "need", "workflow"],
        "team_fit": ["founder", "team", "advantage", "experience", "capability"],
        "timing": ["timing", "now", "quarter", "window", "macro", "launch"],
        "funding": ["funding", "runway", "budget", "capital", "round", "finance"],
        "channel_roi": ["roi", "conversion", "pipeline", "meetings", "paid", "channel"],
        "audience_fit": ["segment", "audience", "persona", "customer", "target"],
        "brand_awareness": ["brand", "awareness", "thought leadership", "positioning"],
        "budget_efficiency": ["budget", "cpa", "cost", "efficiency", "roi"],
        "audience_intent": ["audience", "intent", "subscriber", "retention"],
        "format_fit": ["format", "video", "newsletter", "article", "podcast"],
        "distribution": ["channel", "distribution", "platform", "owned", "paid"],
        "production_feasibility": ["cadence", "production", "team", "cost", "schedule"],
        "urgency": ["urgent", "blocking", "constrained", "risk", "now"],
        "budget_fit": ["budget", "salary", "burn", "cost", "finance"],
        "market_salary": ["salary", "senior", "market", "compensation", "contract"],
        "team_gap": ["gap", "capability", "team", "throughput", "architecture"],
        "risk_return": ["return", "downside", "upside", "risk", "liquidity"],
        "exit_probability": ["exit", "liquidity", "stop", "funding", "sell"],
        "market_timing": ["timing", "macro", "entry", "market", "cycle"],
        "team_quality": ["team", "operator", "track record", "quality", "owner"],
        "strategic_fit": ["strategic", "fit", "priority", "objective", "alignment"],
        "evidence_quality": ["evidence", "proof", "metrics", "validated", "data"],
        "reversibility": ["reversible", "pause", "stop", "fallback", "option"],
        "execution_readiness": ["owner", "plan", "timeline", "resources", "stakeholders"],
    }
    score = evidence + _keyword_score(combined, dimension_keywords.get(key, []))

    if key in {"effort", "budget_fit", "budget_efficiency", "funding"}:
        score += 10 if request.budget > 0 else -6
    if key in {"confidence", "evidence_quality"} and request.known_risks:
        score += 5
    if key in {"urgency", "timing", "market_timing"} and request.timeline:
        score += 6
    if key in {"team_fit", "team_gap", "team_quality", "execution_readiness"} and request.stakeholders:
        score += 7

    final_score = _bounded_score(score)
    reason = "Strong supporting signals" if final_score >= 75 else "Moderate support with validation needs" if final_score >= 60 else "Evidence gap requires follow-up"
    return final_score, reason


def _build_scoring_summary(request: DecisionRequest, options: list[str]) -> ScoringSummary:
    model = PACK_SCORING_MODELS[request.pack]
    dimensions: list[ScoringDimension] = []
    for key, label, weight in model["dimensions"]:  # type: ignore[index]
        score, reason = _score_dimension(str(key), request, options)
        dimensions.append(ScoringDimension(key=str(key), label=str(label), weight=float(weight), score=score, reason=reason))

    total = _bounded_score(sum(item.score * item.weight for item in dimensions))
    if request.language == "zh":
        recommendation = "建议推进并设置验证门" if total >= 75 else "建议小范围试点后再放大" if total >= 60 else "建议暂缓，先补充关键证据"
    else:
        recommendation = "Proceed with staged execution" if total >= 75 else "Run a constrained validation pilot" if total >= 60 else "Pause and gather stronger evidence"

    return ScoringSummary(
        pack=request.pack,
        framework=str(model["framework"]),
        prompt=str(model["prompt"]),
        extracted_signals=_extract_decision_signals(request, options),
        dimensions=dimensions,
        total_score=total,
        recommendation=recommendation,
    )


def _timeline_months(value: str) -> float:
    lowered = value.lower()
    number_match = re.search(r"(\d+(?:\.\d+)?)", lowered)
    if not number_match:
        return 0
    number = float(number_match.group(1))
    if any(unit in lowered for unit in ["day", "天"]):
        return number / 30
    if any(unit in lowered for unit in ["week", "周"]):
        return number / 4
    if any(unit in lowered for unit in ["year", "年"]):
        return number * 12
    if "quarter" in lowered or "季度" in lowered:
        return number * 3
    return number


def _request_tags(request: DecisionRequest, options: list[str]) -> set[str]:
    text = " ".join(
        [
            request.title,
            request.context,
            request.objective,
            request.constraints,
            request.stakeholders,
            request.success_metrics,
            request.known_risks,
            " ".join(options),
        ]
    ).lower()
    candidate_tags = {tag for business_case in BUSINESS_CASES for tag in business_case.tags}
    matched = {tag for tag in candidate_tags if tag.lower() in text}
    pack_defaults = {
        "Product": {"launch", "activation", "workflow"},
        "Startup": {"growth", "market", "wedge"},
        "Marketing": {"brand", "pipeline", "growth"},
        "Content": {"audience", "distribution", "cadence"},
        "Hiring": {"team", "talent", "process"},
        "Investment": {"risk", "market", "capital"},
        "Custom": {"strategy", "retention", "platform"},
    }
    return matched | pack_defaults.get(request.pack, set())


def _match_reference_cases(request: DecisionRequest, options: list[str], limit: int = 3) -> list[MatchedBusinessCase]:
    tags = _request_tags(request, options)
    request_months = _timeline_months(request.timeline)
    scored: list[MatchedBusinessCase] = []

    for business_case in BUSINESS_CASES:
        score = 0.0
        if business_case.pack == request.pack:
            score += 45
        elif business_case.pack in {"Custom", "Content"}:
            score += 8

        overlap = tags.intersection(set(business_case.tags))
        score += min(30, len(overlap) * 8)

        if request.budget > 0 and business_case.budget > 0:
            ratio = min(request.budget, business_case.budget) / max(request.budget, business_case.budget)
            score += ratio * 15
        else:
            score += 5

        case_months = _timeline_months(business_case.timeline)
        if request_months and case_months:
            timeline_gap = abs(request_months - case_months)
            score += max(0, 10 - min(10, timeline_gap))
        else:
            score += 4

        scored.append(MatchedBusinessCase(**business_case.dict(), similarity=max(0, min(100, round(score)))))

    return sorted(scored, key=lambda item: item.similarity, reverse=True)[:limit]


def _remember_report(report: DecisionReport) -> DecisionReport:
    REPORT_STORE[report.report_id] = report
    return report


def _safe_filename(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_") or "decision_report"


def _report_markdown(report: DecisionReport) -> str:
    lines = [
        f"# DecisionOS Report: {report.report_id}",
        "",
        f"- Pack: {report.pack}",
        f"- Created: {report.created_at}",
        "",
        "## Executive Summary",
        report.executive_summary,
        "",
        "## Decision Verdict",
        report.decision_verdict,
        "",
        "## Scoring Engine",
        f"- Framework: {report.scoring_summary.framework}",
        f"- Total Score: {report.scoring_summary.total_score}/100",
        f"- Recommendation: {report.scoring_summary.recommendation}",
        "",
    ]
    for dimension in report.scoring_summary.dimensions:
        lines.append(f"- {dimension.label}: {dimension.score}/100, weight {dimension.weight:.0%}. {dimension.reason}")

    lines += ["", "## Reference Cases"]
    for business_case in report.reference_cases:
        lines += [
            f"### {business_case.title}",
            f"- Company: {business_case.company}",
            f"- Year: {business_case.year}",
            f"- Similarity: {business_case.similarity}%",
            f"- Lesson: {business_case.lesson}",
            "",
        ]

    sections = [
        ("Core Value", report.core_value),
        ("Benchmark", report.benchmark),
        ("Execution Plan", report.execution_plan),
        ("Budget", report.budget),
        ("Next Actions", report.next_actions),
    ]
    for title, items in sections:
        lines += ["", f"## {title}"]
        lines.extend(f"- {item}" for item in items)

    lines += ["", "## Risk Matrix"]
    for risk in report.risk_matrix:
        lines.append(f"- {risk.risk}: likelihood {risk.likelihood}, impact {risk.impact}. Mitigation: {risk.mitigation}")

    lines += ["", "## Timeline"]
    for item in report.timeline:
        lines.append(f"- {item.phase} ({item.window}): {item.output}")

    lines += ["", "## This Week Action List"]
    for item in report.action_items:
        lines.append(f"- [{item.priority}] {item.day}: {item.task} Owner: {item.owner}. Duration: {item.duration}.")

    return "\n".join(lines).strip() + "\n"


def _pdf_paragraph(text: object, style: str = "DecisionBody") -> Paragraph:
    return Paragraph(str(text).replace("\n", "<br/>"), PDF_STYLES[style])


def _build_decision_pdf(report: DecisionReport, path: Path) -> Path:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"DecisionOS {report.report_id}",
    )
    story = [
        _pdf_paragraph(f"DecisionOS Report: {report.report_id}", "DecisionTitle"),
        _pdf_paragraph(f"Pack: {report.pack} | Created: {report.created_at}"),
        Spacer(1, 5 * mm),
        _pdf_paragraph("Executive Summary", "DecisionHeading"),
        _pdf_paragraph(report.executive_summary),
        _pdf_paragraph("Decision Verdict", "DecisionHeading"),
        _pdf_paragraph(report.decision_verdict),
        _pdf_paragraph("Scoring Engine", "DecisionHeading"),
        _pdf_paragraph(f"{report.scoring_summary.framework}: {report.scoring_summary.total_score}/100"),
    ]
    for dimension in report.scoring_summary.dimensions:
        story.append(_pdf_paragraph(f"- {dimension.label}: {dimension.score}/100 | weight {dimension.weight:.0%} | {dimension.reason}"))

    story.append(_pdf_paragraph("Reference Cases", "DecisionHeading"))
    for business_case in report.reference_cases:
        story.append(_pdf_paragraph(f"{business_case.title} ({business_case.company}, {business_case.year}) - {business_case.similarity}%"))
        story.append(_pdf_paragraph(f"Lesson: {business_case.lesson}"))

    export_sections = [
        ("Core Value", report.core_value),
        ("Benchmark", report.benchmark),
        ("Execution Plan", report.execution_plan),
        ("Budget", report.budget),
        ("Next Actions", report.next_actions),
    ]
    for title, items in export_sections:
        story.append(_pdf_paragraph(title, "DecisionHeading"))
        for item in items:
            story.append(_pdf_paragraph(f"- {item}"))

    story.append(_pdf_paragraph("Risk Matrix", "DecisionHeading"))
    for risk in report.risk_matrix:
        story.append(_pdf_paragraph(f"- {risk.risk}: {risk.likelihood}/{risk.impact}. {risk.mitigation}"))

    story.append(_pdf_paragraph("Timeline", "DecisionHeading"))
    for item in report.timeline:
        story.append(_pdf_paragraph(f"- {item.phase} ({item.window}): {item.output}"))

    story.append(_pdf_paragraph("This Week Action List", "DecisionHeading"))
    for item in report.action_items:
        story.append(_pdf_paragraph(f"- [{item.priority}] {item.day}: {item.task} Owner: {item.owner}. Duration: {item.duration}."))

    doc.build(story)
    return path


def _feedback_topics(feedback: str) -> set[str]:
    lowered = feedback.lower()
    topics: set[str] = set()
    if any(term in lowered for term in ["budget", "cost", "funding", "资金", "预算", "成本"]):
        topics.add("budget")
    if any(term in lowered for term in ["risk", "downside", "unsafe", "风险", "下行"]):
        topics.add("risk")
    if any(term in lowered for term in ["evidence", "data", "proof", "assumption", "证据", "数据", "假设"]):
        topics.add("evidence")
    if any(term in lowered for term in ["disagree", "oppose", "not agree", "too optimistic", "不同意", "反对", "过于乐观"]):
        topics.add("verdict")
    if any(term in lowered for term in ["timeline", "delay", "schedule", "时间", "延期", "周期"]):
        topics.add("timeline")
    return topics or {"evidence"}


def _apply_feedback(report: DecisionReport, feedback: str) -> tuple[DecisionReport, list[FeedbackChange]]:
    updated = report.copy(deep=True)
    topics = _feedback_topics(feedback)
    changes: list[FeedbackChange] = []
    is_zh = any("\u4e00" <= char <= "\u9fff" for char in feedback)

    def add_change(section: str, before: str, after: str, reason: str) -> None:
        changes.append(FeedbackChange(section=section, before=before, after=after, reason=reason))

    if "verdict" in topics or "evidence" in topics:
        before = updated.decision_verdict
        if is_zh:
            updated.decision_verdict = f"已根据用户异议下调为审慎推进：先补充反驳中提到的证据，再决定是否放大。原判断参考：{before}"
        else:
            updated.decision_verdict = f"Revised after user challenge: proceed only after validating the objection. Original view: {before}"
        add_change("decision_verdict", before, updated.decision_verdict, "Feedback challenged the strength of the original conclusion.")

    if "budget" in topics:
        before = " | ".join(updated.budget)
        updated.budget = [
            *updated.budget,
            "用户反馈指出预算/成本存在不确定性，下一阶段预算应拆成验证预算和放大预算。" if is_zh else "User feedback flags budget or cost uncertainty; split the next tranche into validation budget and scale budget.",
        ]
        add_change("budget", before, " | ".join(updated.budget), "Feedback introduced budget or cost constraints.")

    if "risk" in topics or "evidence" in topics:
        before = "; ".join(item.risk for item in updated.risk_matrix)
        updated.risk_matrix.append(
            RiskItem(
                risk="用户反驳中的新增风险" if is_zh else "New risk from user objection",
                likelihood="待验证" if is_zh else "To validate",
                impact="高" if is_zh else "High",
                mitigation=("将用户异议转化为验证假设，指定负责人和截止时间。" if is_zh else "Convert the objection into a validation hypothesis with owner and due date."),
            )
        )
        add_change("risk_matrix", before, "; ".join(item.risk for item in updated.risk_matrix), "Feedback added a material risk or evidence gap.")

    if "timeline" in topics:
        before = "; ".join(f"{item.phase}:{item.window}" for item in updated.timeline)
        updated.timeline.insert(
            1,
            TimelineItem(
                phase="反驳验证" if is_zh else "Objection validation",
                window="48 小时" if is_zh else "48 hours",
                output="验证用户异议是否改变结论" if is_zh else "Validate whether the objection changes the verdict",
            ),
        )
        add_change("timeline", before, "; ".join(f"{item.phase}:{item.window}" for item in updated.timeline), "Feedback affects timing or schedule confidence.")

    before_score = updated.scoring_summary.total_score
    score_delta = 10 if {"verdict", "risk", "evidence"} & topics else 5
    updated.scoring_summary.total_score = max(0, before_score - score_delta)
    for dimension in updated.scoring_summary.dimensions:
        if dimension.key in {"confidence", "evidence_quality", "risk_return", "budget_fit", "budget_efficiency", "funding", "market_timing", "channel_roi"}:
            dimension.score = max(0, dimension.score - score_delta)
            dimension.reason = "Adjusted after user objection"
    updated.scoring_summary.recommendation = (
        "建议先验证用户异议，再决定是否推进" if is_zh else "Validate the user objection before scaling the decision"
    )
    add_change("scoring_summary", f"{before_score}/100", f"{updated.scoring_summary.total_score}/100", "Feedback reduced confidence in the weighted score.")

    before_benchmark = " | ".join(updated.benchmark)
    updated.benchmark = [
        (f"当前加权总分：{updated.scoring_summary.total_score}/100。" if item.startswith("当前加权总分") else f"Current weighted score: {updated.scoring_summary.total_score}/100." if item.startswith("Current weighted score") else item)
        for item in updated.benchmark
    ]
    if before_benchmark != " | ".join(updated.benchmark):
        add_change("benchmark", before_benchmark, " | ".join(updated.benchmark), "Benchmark score was synchronized with the revised scoring summary.")

    before_actions = " | ".join(updated.next_actions)
    feedback_action = "把用户异议写成可验证假设，并指定负责人。" if is_zh else "Convert the user objection into a testable hypothesis with an owner."
    if feedback_action not in updated.next_actions:
        updated.next_actions = [feedback_action, *updated.next_actions]
        add_change("next_actions", before_actions, " | ".join(updated.next_actions), "Feedback requires a new validation action.")

    updated.reasoning_timeline.append(
        ReasoningStep(
            label="反驳评估" if is_zh else "Feedback review",
            focus="评估用户异议并局部更新报告" if is_zh else "Evaluate objection and update affected report sections",
            signal=feedback,
            status="已更新" if is_zh else "Updated",
        )
    )
    return updated, changes


def _format_form_data(form_data: dict[str, object]) -> list[str]:
    labels = {
        "title": "Decision title",
        "pack": "Pack",
        "context": "Strategic context",
        "objective": "Decision objective",
        "options": "Options under review",
        "constraints": "Constraints",
        "budget": "Budget",
        "timeline": "Time horizon",
        "stakeholders": "Stakeholders",
        "success_metrics": "Success metrics",
        "known_risks": "Known risks",
    }
    lines: list[str] = []
    for key, label in labels.items():
        value = form_data.get(key)
        if value in (None, "", []):
            continue
        if isinstance(value, list):
            rendered = ", ".join(str(item) for item in value if str(item).strip())
        else:
            rendered = str(value).strip()
        if rendered:
            lines.append(f"{label}: {rendered}")
    return lines


def _build_action_items(request: DecisionRequest, language: DecisionLanguage) -> list[ActionItem]:
    _ = ACTION_LIST_PROMPT_INSTRUCTION
    if language == "zh":
        return [
            ActionItem(day="周一", task="完成一页决策简报，锁定目标、选项、约束和判断标准", owner=request.stakeholders or "决策负责人", duration="2 小时", priority="高"),
            ActionItem(day="周二", task="访谈 3 个关键用户或相关方，补齐最关键证据", owner="证据负责人", duration="半天", priority="高"),
            ActionItem(day="周三", task="对主路径和备选路径做成本、风险、可逆性评分", owner="运营负责人", duration="2 小时", priority="中"),
            ActionItem(day="周四", task="设计最小验证试点和通过/停止条件", owner="执行负责人", duration="半天", priority="高"),
            ActionItem(day="周五", task="召开决策复盘会，确认放大、修正、暂停或停止", owner="最终决策人", duration="1 小时", priority="中"),
        ]

    return [
        ActionItem(day="Monday", task="Complete a one-page decision brief with objective, options, constraints, and decision criteria.", owner=request.stakeholders or "Decision owner", duration="2 hours", priority="High"),
        ActionItem(day="Tuesday", task="Interview 3 key users or stakeholders to fill the highest-risk evidence gap.", owner="Evidence owner", duration="Half day", priority="High"),
        ActionItem(day="Wednesday", task="Score the lead path and fallback path by cost, risk, reversibility, and time-to-proof.", owner="Operations owner", duration="2 hours", priority="Medium"),
        ActionItem(day="Thursday", task="Design the smallest validation pilot with pass/fail gates.", owner="Execution owner", duration="Half day", priority="High"),
        ActionItem(day="Friday", task="Run the decision review and choose scale, revise, pause, or stop.", owner="Final decision owner", duration="1 hour", priority="Medium"),
    ]


@router.post("/generate-followups", response_model=FollowUpSession)
def generate_followups(request: FollowUpRequest) -> FollowUpSession:
    digest_source = f"{request.pack}|{request.formData.get('title', '')}|{datetime.utcnow().isoformat()}"
    decision_id = f"decision_{sha1(digest_source.encode('utf-8')).hexdigest()[:10]}"
    questions = [question.copy(deep=True) for question in (FOLLOWUP_TEMPLATES_ZH if request.formData.get('language') == 'zh' else FOLLOWUP_TEMPLATES)[request.pack]]
    FOLLOWUP_SESSIONS[decision_id] = {
        "pack": request.pack,
        "formData": request.formData,
        "questions": questions,
        "status": "answering",
    }
    return FollowUpSession(decisionId=decision_id, questions=questions, status="answering")


@router.post("/submit-answers", response_model=SubmitFollowUpAnswersResponse)
def submit_followup_answers(request: SubmitFollowUpAnswersRequest) -> SubmitFollowUpAnswersResponse:
    session = FOLLOWUP_SESSIONS.get(request.decisionId, {})
    form_data = session.get("formData", {})
    questions = session.get("questions", [])
    answer_map = {answer.id: answer.answer.strip() for answer in request.answers}

    lines = ["Original decision inputs:"]
    if isinstance(form_data, dict):
        lines.extend(_format_form_data(form_data))

    lines.append("")
    lines.append("Follow-up answers:")
    if isinstance(questions, list):
        for question in questions:
            if isinstance(question, FollowUpQuestion):
                answer = answer_map.get(question.id, "")
                if answer:
                    lines.append(f"{question.question}: {answer}")
    else:
        for answer in request.answers:
            if answer.answer.strip():
                lines.append(f"{answer.id}: {answer.answer.strip()}")

    combined_context = "\n".join(line for line in lines if line is not None).strip()
    if session:
        session["status"] = "completed"
        session["answers"] = request.answers

    return SubmitFollowUpAnswersResponse(decisionId=request.decisionId, combined_context=combined_context, status="completed")


@router.post("/generate", response_model=DecisionReport)
def generate_decision(request: DecisionRequest) -> DecisionReport:
    options = _split_options(request.options)
    digest = sha1(f"{request.title}|{request.pack}|{datetime.utcnow().isoformat()}".encode("utf-8")).hexdigest()[:10]
    budget_text = f"{request.budget:,.0f}" if request.budget > 0 else ("未固定" if request.language == "zh" else "not fixed")
    primary_option = options[0]
    scoring_summary = _build_scoring_summary(request, options)
    reference_cases = _match_reference_cases(request, options)

    if request.language == "zh":
        lens = PACK_LENS_ZH[request.pack]
        verdict = scoring_summary.recommendation
        objective = _clean_sentence(request.objective)
        return _remember_report(DecisionReport(
            report_id=f"decision_{digest}",
            created_at=datetime.utcnow().isoformat(),
            pack=request.pack,
            executive_summary=(
                f"{request.title} 应被当作一套决策系统来处理，而不是一次性任务。"
                f"当前建议是：{verdict}。{scoring_summary.framework} 加权总分为 {scoring_summary.total_score}/100，"
                f"核心判断维度为{lens['benchmark']}。"
            ),
            decision_verdict=f"{verdict}：以“{primary_option}”作为主路径，并依据 {scoring_summary.framework} 评分设置明确证据门。",
            core_value=[
                lens["value"],
                f"围绕目标对齐相关方：{objective}。",
                "通过拆分假设、约束和可衡量证据，减少不必要的执行浪费。",
            ],
            benchmark=[
                f"评分框架：{scoring_summary.framework}。",
                f"将主路径与以下 Pack 维度比较：{lens['benchmark']}。",
                f"当前加权总分：{scoring_summary.total_score}/100。",
                "强决策应当具体、可衡量、尽量可逆，并由明确负责人推动。",
            ],
            risk_matrix=[
                RiskItem(
                    risk="证据质量不足",
                    likelihood="中",
                    impact="高",
                    mitigation="在投入完整资源前，先定义最小可验证证据包。",
                ),
                RiskItem(
                    risk="执行被稀释",
                    likelihood="中",
                    impact="中",
                    mitigation="第一轮只保留一个负责人、一个核心指标和一个复盘节奏。",
                ),
                RiskItem(
                    risk=request.known_risks or "相关方风险未被充分说明",
                    likelihood="未知",
                    impact="高",
                    mitigation="把开放风险转化为带负责人和验证日期的假设。",
                ),
            ],
            execution_plan=[
                "界定决策：确认负责人、目标、选项、约束和不可妥协条件。",
                "收集证据：访谈用户或相关方，评估财务影响，并验证可执行性。",
                "评估选项：比较收益、下行风险、验证速度、成本、可逆性和战略匹配度。",
                "运行受控试点：执行能够验证核心假设的最小版本。",
                "进入下一决策门：根据约定指标决定放大、修正、暂停或停止。",
            ],
            budget=[
                f"当前规划预算：{budget_text}。",
                "建议 60% 用于核心执行，20% 用于验证和度量，20% 用作风险缓冲。",
                "在验证门通过前，不释放下一阶段预算。",
            ],
            timeline=[
                TimelineItem(phase="界定", window="第 1-2 天", output="决策简报和选项清单"),
                TimelineItem(phase="验证", window=request.timeline or "第 1-2 周", output="证据复盘和试点设计"),
                TimelineItem(phase="承诺", window="下一次决策评审", output="放大、修正、暂停或停止"),
            ],
            next_actions=[
                "形成一页决策简报，明确负责人、目标、选项、约束和指标。",
                "选择主路径和一个备选路径。",
                "复核 Pack 评分中低于 70 分的维度，并补充证据。",
                "定义验证门，并安排决策复盘时间。",
                "分别指定证据、执行、财务和风险负责人。",
            ],
            action_items=_build_action_items(request, request.language),
            scoring_summary=scoring_summary,
            reference_cases=reference_cases,
            reasoning_timeline=[
                ReasoningStep(label="信息提取", focus="LLM 提取关键信号", signal="；".join(scoring_summary.extracted_signals), status="已解析"),
                ReasoningStep(label="评分模型", focus=f"套用 {scoring_summary.framework}", signal=scoring_summary.prompt, status="已选择"),
                ReasoningStep(label="维度打分", focus="按 Pack 维度生成 0-100 分", signal="；".join(f"{DIMENSION_LABELS_ZH.get(item.key, item.label)} {item.score}" for item in scoring_summary.dimensions), status="已评分"),
                ReasoningStep(label="案例对标", focus="匹配相似商业案例", signal="；".join(f"{CASE_TITLES_ZH.get(item.id, item.company)} {item.similarity}%" for item in reference_cases), status="已匹配"),
                ReasoningStep(label="加权计算", focus="按权重计算总分", signal=f"{scoring_summary.total_score}/100", status="已计算"),
                ReasoningStep(label="结论", focus="形成分阶段建议", signal=verdict, status="就绪"),
            ],
        ))

    lens = PACK_LENS[request.pack]
    verdict = scoring_summary.recommendation
    objective = _clean_sentence(request.objective)

    return _remember_report(DecisionReport(
        report_id=f"decision_{digest}",
        created_at=datetime.utcnow().isoformat(),
        pack=request.pack,
        executive_summary=(
            f"{request.title} should be treated as a decision system, not a one-off task. "
            f"The current recommendation is: {verdict}. The {scoring_summary.framework} weighted score is "
            f"{scoring_summary.total_score}/100, based on {lens['benchmark']}."
        ),
        decision_verdict=f"{verdict}: choose '{primary_option}' as the lead path, with evidence gates tied to the {scoring_summary.framework} score.",
        core_value=[
            lens["value"],
            f"Align stakeholders around the objective: {objective}.",
            "Reduce avoidable execution waste by separating assumptions, constraints, and measurable proof.",
        ],
        benchmark=[
            f"Scoring framework: {scoring_summary.framework}.",
            f"Compare the leading option against pack dimensions: {lens['benchmark']}.",
            f"Current weighted score: {scoring_summary.total_score}/100.",
            "A strong decision should be specific, measurable, reversible where possible, and owned by a named team.",
        ],
        risk_matrix=[
            RiskItem(
                risk="Evidence quality",
                likelihood="Medium",
                impact="High",
                mitigation="Define the smallest proof package before committing full resources.",
            ),
            RiskItem(
                risk="Execution dilution",
                likelihood="Medium",
                impact="Medium",
                mitigation="Limit the first cycle to one owner, one operating metric, and one review cadence.",
            ),
            RiskItem(
                risk=request.known_risks or "Unstated stakeholder risk",
                likelihood="Unknown",
                impact="High",
                mitigation="Convert open risks into named assumptions with validation dates.",
            ),
        ],
        execution_plan=[
            "Frame the decision: confirm owner, objective, options, constraints, and non-negotiables.",
            "Collect evidence: interview users or stakeholders, review financial impact, and test feasibility.",
            "Score options: compare upside, downside, time-to-proof, cost, reversibility, and strategic fit.",
            "Run a controlled pilot: execute the smallest version that can prove or disprove the main thesis.",
            "Decide the next gate: scale, revise, pause, or stop based on agreed metrics.",
        ],
        budget=[
            f"Current planning budget: {budget_text}.",
            "Reserve 60% for core execution, 20% for validation and measurement, 20% for contingency.",
            "Do not unlock the next budget tranche until the validation gate is passed.",
        ],
        timeline=[
            TimelineItem(phase="Frame", window="Day 1-2", output="Decision brief and option set"),
            TimelineItem(phase="Validate", window=request.timeline or "Week 1-2", output="Evidence review and pilot design"),
            TimelineItem(phase="Commit", window="Next review cycle", output="Scale, revise, pause, or stop decision"),
        ],
        next_actions=[
            "Create a one-page decision brief with owner, objective, options, constraints, and metrics.",
            "Select the lead option and one fallback option.",
            "Review scoring dimensions below 70 and fill the evidence gaps.",
            "Define the validation gate and schedule the decision review.",
            "Assign owners for evidence, execution, finance, and risk.",
        ],
        action_items=_build_action_items(request, request.language),
        scoring_summary=scoring_summary,
        reference_cases=reference_cases,
        reasoning_timeline=[
            ReasoningStep(label="Extraction", focus="LLM extracts key decision signals", signal="; ".join(scoring_summary.extracted_signals), status="Parsed"),
            ReasoningStep(label="Model", focus=f"Apply {scoring_summary.framework}", signal=scoring_summary.prompt, status="Selected"),
            ReasoningStep(label="Scoring", focus="Score each pack dimension from 0-100", signal="; ".join(f"{item.label} {item.score}" for item in scoring_summary.dimensions), status="Scored"),
            ReasoningStep(label="Case Match", focus="Match similar business cases", signal="; ".join(f"{item.company} {item.similarity}%" for item in reference_cases), status="Matched"),
            ReasoningStep(label="Weighting", focus="Calculate weighted total score", signal=f"{scoring_summary.total_score}/100", status="Calculated"),
            ReasoningStep(label="Verdict", focus="Recommend a staged decision", signal=verdict, status="Ready"),
        ],
    ))


@router.post("/feedback", response_model=DecisionFeedbackResponse)
def update_decision_with_feedback(request: DecisionFeedbackRequest) -> DecisionFeedbackResponse:
    report = REPORT_STORE.get(request.decisionId)
    if report is None:
        raise HTTPException(status_code=404, detail="Decision report not found. Generate a report before submitting feedback.")

    updated_report, changes = _apply_feedback(report, request.feedback)
    REPORT_STORE[request.decisionId] = updated_report
    return DecisionFeedbackResponse(changes=changes, updatedReport=updated_report)


@router.get("/{decision_id}/export")
def export_decision_report(decision_id: str, format: ExportFormat = Query("pdf")) -> FileResponse:
    report = REPORT_STORE.get(decision_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Decision report not found. Generate a report before exporting.")

    ensure_report_dir()
    report_dir = Path(REPORT_DIR)
    filename_base = _safe_filename(f"DecisionOS_{decision_id}")

    if format == "markdown":
        path = report_dir / f"{filename_base}.md"
        path.write_text(_report_markdown(report), encoding="utf-8")
        return FileResponse(path, media_type="text/markdown; charset=utf-8", filename=path.name)

    path = report_dir / f"{filename_base}.pdf"
    _build_decision_pdf(report, path)
    return FileResponse(path, media_type="application/pdf", filename=path.name)
