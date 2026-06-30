"use client";

import { ArrowRight, BrainCircuit, CheckCircle2, ClipboardList, Copy, Download, FileText, Loader2, Plus, ShieldAlert, Sparkles, UploadCloud } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { ActionList } from "@/components/ActionList";
import { FollowUpStep } from "@/components/FollowUpStep";
import { TopNav } from "@/components/top-nav";
import { decisionTemplateExamples } from "@/lib/decision-templates";
import type { DecisionPack, DecisionReport, DecisionRequest, FeedbackChange, FollowUpSession } from "@/lib/types";

type Locale = "en" | "zh";
type InputMode = "manual" | "template" | "upload";

type UploadParseResponse = {
  parsed: DecisionRequest;
  extracted_text: string;
  confidence: number;
  field_sources: Array<{
    field: string;
    label: string;
    value: string;
    source_excerpt: string;
    confidence: number;
  }>;
  warnings: string[];
};

const packs: Array<{ name: DecisionPack; description: Record<Locale, string> }> = [
  { name: "Product", description: { en: "Roadmap, feature priority, launch scope", zh: "路线图、功能优先级、发布范围" } },
  { name: "Startup", description: { en: "Market entry, wedge, funding path", zh: "市场进入、切入点、融资路径" } },
  { name: "Marketing", description: { en: "Positioning, channels, growth motion", zh: "定位、渠道、增长动作" } },
  { name: "Content", description: { en: "Audience, format, distribution, cadence", zh: "受众、形式、分发、节奏" } },
  { name: "Hiring", description: { en: "Role design, seniority, timing, budget", zh: "岗位设计、职级、时机、预算" } },
  { name: "Investment", description: { en: "Capital allocation, downside, timing", zh: "资金配置、下行风险、进入时机" } },
  { name: "Custom", description: { en: "Any high-stakes business decision", zh: "任意重大业务决策" } }
];

const packExamples: Record<DecisionPack, DecisionRequest> = {
  Product: {
    title: "是否上线企业 AI 决策工作台模块",
    pack: "Product",
    context: "企业客户需要把分散的项目输入快速转化为可执行决策，但本季度工程资源有限，销售团队也需要更清晰的演示材料。",
    objective: "判断是否现在发布第一版工作台模块，还是等待更深的系统集成。",
    options: ["发布聚焦版 MVP", "等待完整集成", "先与两个设计伙伴试点"],
    constraints: "8 周交付窗口，后端资源有限，必须支持销售演示和客户试用。",
    budget: 180000,
    timeline: "8 周",
    stakeholders: "产品、工程、销售、客户成功",
    success_metrics: "激活率、周活跃团队数、首次生成报告耗时、设计伙伴转化率",
    known_risks: "范围过大可能降低产品质量，并推迟采用证据的形成。"
  },
  Startup: {
    title: "是否进入中型企业运营软件市场",
    pack: "Startup",
    context: "团队在中型企业运营场景中看到重复需求，但该品类已有成熟工作流厂商，切入点和融资叙事仍需验证。",
    objective: "判断是否先做垂直切入，再进入下一轮融资准备。",
    options: ["垂直切入", "直接做横向平台", "服务式验证"],
    constraints: "6 个月内必须形成清晰的融资叙事和付费验证。",
    budget: 320000,
    timeline: "12 周",
    stakeholders: "创始团队、早期客户、投资人",
    success_metrics: "有效商机、付费试点、实施周期、留存信号",
    known_risks: "市场可能需要比团队当前能力更多的实施和交付支持。"
  },
  Marketing: {
    title: "选择下一季度企业获客动作",
    pack: "Marketing",
    context: "当前自然线索稳定，但企业客户转化在不同人群和渠道之间差异明显，预算需要更聚焦。",
    objective: "选择下一个计划周期最有杠杆的获客动作。",
    options: ["ABM 定向活动", "伙伴联合线上会", "高管内容影响力"],
    constraints: "团队小、媒体预算有限，需要一个季度内看到可衡量管道。",
    budget: 120000,
    timeline: "一个季度",
    stakeholders: "市场、销售、收入运营",
    success_metrics: "新增管道、会议率、赢单率、单个商机成本",
    known_risks: "如果没有销售跟进纪律，品牌活动可能难以转化为收入。"
  },
  Content: {
    title: "是否试点专业内容栏目",
    pack: "Content",
    context: "团队已经有内容主题、目标受众、预算估算、渠道组合、发布节奏和商业化假设，但还没有连续内容的真实留存数据。",
    objective: "判断是否先投入小规模试点，再扩展为长期内容项目。",
    options: ["试点 3 期", "直接做完整季", "先测试受众需求"],
    constraints: "制作团队精简，发布时间固定，必须符合品牌安全要求。",
    budget: 90000,
    timeline: "6 周",
    stakeholders: "内容负责人、增长负责人、财务、品牌负责人",
    success_metrics: "完读/完播率、合格订阅、单条内容成本、赞助兴趣",
    known_risks: "创意目标可能超过制作能力，影响稳定发布。"
  },
  Hiring: {
    title: "是否招聘高级平台负责人",
    pack: "Hiring",
    context: "工程吞吐被架构决策拖慢，但公司也在控制现金消耗，需要判断招聘是否是当前最优解。",
    objective: "决定是全职招聘、使用顾问，还是内部重新分工。",
    options: ["招聘高级负责人", "使用兼职顾问", "提拔内部负责人"],
    constraints: "预算敏感、架构问题紧急、面试带宽有限。",
    budget: 260000,
    timeline: "10 周",
    stakeholders: "CEO、CTO、工程经理、财务",
    success_metrics: "架构决策速度、团队吞吐、关键人员流失风险下降",
    known_risks: "过早招聘过高职级可能在组织模型成熟前增加固定成本。"
  },
  Investment: {
    title: "是否投资新的战略资产",
    pack: "Investment",
    context: "该资产可能增强长期位置，但短期流动性、下行敞口和进入时机需要更清晰边界。",
    objective: "决定现在投资、分阶段投入，还是等待更好的进入条件。",
    options: ["现在投资", "分阶段承诺", "等待更好时机"],
    constraints: "流动性目标、董事会审批、宏观环境不确定。",
    budget: 500000,
    timeline: "30 天",
    stakeholders: "财务、战略、董事会、业务负责人",
    success_metrics: "风险调整回报、战略杠杆、流动性影响、下行保护",
    known_risks: "如果市场条件恶化，机会成本可能迅速升高。"
  },
  Custom: {
    title: "解决一个跨部门战略决策",
    pack: "Custom",
    context: "领导团队需要在投入预算、人力和管理注意力之前，获得结构化建议和可执行路径。",
    objective: "把开放问题转化为明确结论、执行计划和下一步动作。",
    options: ["推进", "修正后推进", "暂停"],
    constraints: "资源有限，证据不完整，跨部门目标尚未完全一致。",
    budget: 100000,
    timeline: "4 周",
    stakeholders: "决策负责人、财务、业务团队、最终用户",
    success_metrics: "决策速度、证据质量、执行准备度、风险降低",
    known_risks: "如果负责人不清晰，决策可能继续被延迟。"
  }
};

const text = {
  en: {
    navAction: "New Decision",
    language: "中文",
    eyebrow: "AI Decision Operating System",
    hero:
      "Enterprise AI advisor for high-stakes choices: frame the decision, reason through tradeoffs, and produce an executive-ready operating plan.",
    inputsTitle: "Decision Inputs",
    inputsSubtitle: "Pick a Pack, define the problem, and provide enough evidence for a structured recommendation.",
    inputModes: {
      manual: "Manual Input",
      template: "Start From Template",
      upload: "Upload Existing Plan"
    },
    uploadTitle: "Upload an existing plan",
    uploadBody: "Upload a script, campaign brief, product proposal, hiring plan, investment memo, or other existing business document. DecisionOS will convert it into structured decision inputs.",
    uploadFormats: "Supports .txt, .md, .docx, and text-based .pdf",
    uploadButton: "Parse into inputs",
    uploadLoading: "Parsing document",
    uploadParsed: "Parsed document",
    uploadConfidence: "Confidence",
    uploadApplyHint: "Review the extracted inputs below, then generate follow-up questions.",
    uploadFieldSources: "Extraction preview",
    uploadSource: "Source",
    parserLabel: "💬 Describe your decision in one sentence",
    parserPlaceholder: "e.g. I run a tea shop in Chengdu with 110k monthly revenue, thinking about a second location...",
    parserButton: "Auto-fill",
    parserLoading: "Analyzing...",
    parserError: "Sentence parser unavailable (requires backend Ollama)",
    titleLabel: "Decision Title",
    titlePlaceholder: "What decision needs to be made?",
    packLabel: "Industry Pack",
    contextLabel: "Strategic Context",
    objectiveLabel: "Decision Objective",
    optionsLabel: "Options Under Review",
    budgetLabel: "Budget",
    timelineLabel: "Time Horizon",
    constraintsLabel: "Constraints",
    stakeholdersLabel: "Stakeholders",
    metricsLabel: "Success Metrics",
    risksLabel: "Known Risks",
    submit: "Generate",
    loading: "Preparing questions",
    thinkingTitle: "AI Thinking / Reasoning Timeline",
    lens: "lens",
    reportTitle: "Decision Report",
    reportSubtitle: "Fixed executive structure for every pack.",
    emptyTitle: "Report structure is ready",
    emptyBody: "Generate a decision, answer the follow-up questions, then DecisionOS will populate the executive summary, verdict, risk matrix, budget, timeline, and next actions.",
    errorPrefix: "Decision failed",
    errorFallback: "check that the API service is running on port 8001.",
    errorHint: "If this keeps happening, start the backend at 127.0.0.1:8001 and retry. Also check that required fields are filled.",
    errorTimeout: "Request timed out. The backend may be busy; retry shortly.",
    likelihood: "Likelihood",
    impact: "Impact",
    defaultSteps: [
      { label: "Context", focus: "Waiting for decision context", signal: "No report generated yet", status: "Ready" },
      { label: "Objective", focus: "Map business outcome", signal: "Define the target state", status: "Ready" },
      { label: "Options", focus: "Compare feasible paths", signal: "Add alternatives for review", status: "Ready" },
      { label: "Risk", focus: "Detect constraints and exposure", signal: "Budget, timing, stakeholders, unknowns", status: "Ready" },
      { label: "Verdict", focus: "Convert reasoning into action", signal: "Generate the report", status: "Ready" }
    ],
    reportSections: {
      executive_summary: "Executive Summary",
      decision_verdict: "Decision Verdict",
      core_value: "Core Value",
      scoring_engine: "Scoring Engine",
      reference_cases: "Reference Cases",
      benchmark: "Benchmark",
      risk_matrix: "Risk Matrix",
      execution_plan: "Execution Plan",
      budget: "Budget",
      timeline: "Timeline",
      next_actions: "Next Actions",
      feedback: "Challenge This Decision"
    },
    feedbackPlaceholder: "Challenge the verdict, risks, score, budget, or timing...",
    feedbackSubmit: "Re-evaluate",
    feedbackLoading: "Re-evaluating",
    feedbackChanges: "Updated sections",
    exportLabel: "Export",
    exportPdf: "PDF",
    exportMarkdown: "Markdown",
    copyReport: "Copy report",
    copiedReport: "Copied"
  },
  zh: {
    navAction: "新建决策",
    language: "EN",
    eyebrow: "AI 决策操作系统",
    hero: "面向重大业务决策的企业级 AI 顾问：梳理问题、推演取舍，并输出可给管理层使用的决策报告。",
    inputsTitle: "决策输入",
    inputsSubtitle: "选择行业 Pack，定义业务问题，并提供足够证据，让系统形成结构化建议。",
    inputModes: {
      manual: "手动输入",
      template: "模板开始",
      upload: "上传已有方案"
    },
    uploadTitle: "上传已有方案",
    uploadBody: "上传已经写好的剧本、活动方案、产品方案、招聘计划、投资材料或其他业务文档，DecisionOS 会将其转化为结构化决策输入。",
    uploadFormats: "支持 .txt、.md、.docx 和带文本层的 .pdf",
    uploadButton: "解析为决策输入",
    uploadLoading: "解析文档中",
    uploadParsed: "解析完成",
    uploadConfidence: "置信度",
    uploadApplyHint: "请检查下方自动回填内容，确认后继续生成追问。",
    uploadFieldSources: "解析结果预览",
    uploadSource: "来源片段",
    parserLabel: "💬 用一句话描述你的决策",
    parserPlaceholder: "例如：我在成都开了一家茶饮店月流水11万，想开第二家店...",
    parserButton: "自动填写",
    parserLoading: "分析中...",
    parserError: "一句话解析暂不可用（后端需要 Ollama）",
    titleLabel: "决策标题",
    titlePlaceholder: "需要做什么决策？",
    packLabel: "行业 Pack",
    contextLabel: "战略背景",
    objectiveLabel: "决策目标",
    optionsLabel: "待比较选项",
    budgetLabel: "预算",
    timelineLabel: "时间周期",
    constraintsLabel: "约束条件",
    stakeholdersLabel: "相关方",
    metricsLabel: "成功指标",
    risksLabel: "已知风险",
    submit: "生成",
    loading: "准备追问",
    thinkingTitle: "AI 思考 / 推理时间线",
    lens: "分析视角",
    reportTitle: "决策报告",
    reportSubtitle: "每个 Pack 都使用固定的管理层报告结构。",
    emptyTitle: "报告结构已就绪",
    emptyBody: "点击生成并回答追问后，这里会填充执行摘要、决策结论、风险矩阵、预算、时间线和下一步动作。",
    errorPrefix: "决策生成失败",
    errorFallback: "请确认 8001 后端 API 服务正在运行。",
    errorHint: "如果仍然失败，请先确认后端地址 127.0.0.1:8001 可访问，并检查标题、背景、目标和选项是否已填写。",
    errorTimeout: "请求超时，后端可能正在处理其他请求，请稍后重试。",
    likelihood: "发生概率",
    impact: "影响程度",
    defaultSteps: [
      { label: "背景", focus: "填写决策信息", signal: "填写标题、背景、目标和选项", status: "就绪" },
      { label: "目标", focus: "明确决策目标", signal: "回答 AI 追问的问题", status: "就绪" },
      { label: "选项", focus: "评估可行路径", signal: "AI 进行 Pack 评分", status: "就绪" },
      { label: "风险", focus: "识别约束和风险", signal: "AI 分析风险矩阵", status: "就绪" },
      { label: "结论", focus: "生成决策报告", signal: "输出行动清单", status: "就绪" }
    ],
    reportSections: {
      executive_summary: "执行摘要",
      decision_verdict: "决策结论",
      core_value: "核心价值",
      scoring_engine: "评分引擎",
      reference_cases: "参考案例",
      benchmark: "对标基准",
      risk_matrix: "风险矩阵",
      execution_plan: "执行计划",
      budget: "预算",
      timeline: "时间线",
      next_actions: "下一步动作",
      feedback: "反驳这个决策"
    },
    feedbackPlaceholder: "对结论、风险、评分、预算或时间提出异议...",
    feedbackSubmit: "重新评估",
    feedbackLoading: "评估中",
    feedbackChanges: "已更新区块",
    exportLabel: "导出",
    exportPdf: "PDF 文档",
    exportMarkdown: "Markdown 文档",
    copyReport: "复制全文",
    copiedReport: "已复制"
  }
};

const reportSectionKeys = [
  "executive_summary",
  "decision_verdict",
  "core_value",
  "benchmark",
  "risk_matrix",
  "execution_plan",
  "budget",
  "timeline",
  "next_actions"
] as const;

const defaultLocaleVersion = "zh-default-2026-06-28";

function getVerdictStrength(score: number, verdict: string, locale: Locale) {
  const lowerVerdict = verdict.toLowerCase();
  if (score >= 80 || lowerVerdict.includes("strong") || verdict.includes("强烈")) {
    return {
      label: locale === "zh" ? "强烈推进" : "Strong Go",
      className: "strong"
    };
  }
  if (score >= 65 || lowerVerdict.includes("pilot") || verdict.includes("试点")) {
    return {
      label: locale === "zh" ? "建议试点" : "Pilot First",
      className: "pilot"
    };
  }
  if (score >= 50 || lowerVerdict.includes("wait") || lowerVerdict.includes("pause") || verdict.includes("暂缓")) {
    return {
      label: locale === "zh" ? "暂缓观察" : "Wait / Revise",
      className: "wait"
    };
  }
  return {
    label: locale === "zh" ? "不建议推进" : "No Go",
    className: "stop"
  };
}

async function getResponseError(response: Response) {
  try {
    const data = await response.json();
    return typeof data?.detail === "string" ? data.detail : `Service returned ${response.status}`;
  } catch {
    return `Service returned ${response.status}`;
  }
}

const API_TIMEOUT = 25000; // 25s

async function fetchWithTimeout(url: string, options: RequestInit = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_TIMEOUT);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    return response;
  } finally {
    clearTimeout(timer);
  }
}

function splitOptions(value: string) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatReportText(report: DecisionReport) {
  return [
    `DecisionOS Report: ${report.report_id}`,
    `Pack: ${report.pack}`,
    "",
    "Executive Summary",
    report.executive_summary,
    "",
    "Decision Verdict",
    report.decision_verdict,
    "",
    "Scoring Engine",
    `${report.scoring_summary.framework}: ${report.scoring_summary.total_score}/100`,
    ...report.scoring_summary.dimensions.map((dimension) => `- ${dimension.label}: ${dimension.score}/100, weight ${Math.round(dimension.weight * 100)}%, ${dimension.reason}`),
    "",
    "Reference Cases",
    ...report.reference_cases.map((businessCase) => `- ${businessCase.title} (${businessCase.company}, ${businessCase.year}) ${businessCase.similarity}%: ${businessCase.lesson}`),
    "",
    "Core Value",
    ...report.core_value.map((item) => `- ${item}`),
    "",
    "Benchmark",
    ...report.benchmark.map((item) => `- ${item}`),
    "",
    "Risk Matrix",
    ...report.risk_matrix.map((risk) => `- ${risk.risk}: ${risk.likelihood}/${risk.impact}. ${risk.mitigation}`),
    "",
    "Execution Plan",
    ...report.execution_plan.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Budget",
    ...report.budget.map((item) => `- ${item}`),
    "",
    "Timeline",
    ...report.timeline.map((item) => `- ${item.phase} (${item.window}): ${item.output}`),
    "",
    "Next Actions",
    ...report.next_actions.map((item) => `- ${item}`),
    "",
    "This Week Action List",
    ...report.action_items.map((item) => `- [${item.priority}] ${item.day}: ${item.task} Owner: ${item.owner}. Duration: ${item.duration}.`)
  ].join("\n");
}

export default function Home() {
  const [form, setForm] = useState<DecisionRequest>(packExamples.Product);
  const [optionsText, setOptionsText] = useState(packExamples.Product.options.join("\n"));
  const [report, setReport] = useState<DecisionReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [followUpLoading, setFollowUpLoading] = useState(false);
  const [followUpSession, setFollowUpSession] = useState<FollowUpSession | null>(null);
  const [followUpAnswers, setFollowUpAnswers] = useState<Record<string, string>>({});
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackChanges, setFeedbackChanges] = useState<FeedbackChange[]>([]);
  const [error, setError] = useState("");
  const [locale, setLocale] = useState<Locale>("zh");
  const [sentenceInput, setSentenceInput] = useState("");
  const [parsing, setParsing] = useState(false);
  const [inputMode, setInputMode] = useState<InputMode>("manual");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadParsing, setUploadParsing] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadParseResponse | null>(null);

  const selectedPack = useMemo(() => packs.find((pack) => pack.name === form.pack) ?? packs[0], [form.pack]);
  const copy = text[locale];

  useEffect(() => {
    let nextLocale: Locale = "zh";
    const version = window.localStorage.getItem("decisionos.defaultLocaleVersion");
    if (version !== defaultLocaleVersion) {
      window.localStorage.setItem("decisionos.locale", "zh");
      window.localStorage.setItem("decisionos.defaultLocaleVersion", defaultLocaleVersion);
    } else {
      const saved = window.localStorage.getItem("decisionos.locale");
      if (saved === "zh" || saved === "en") {
        nextLocale = saved;
      }
    }

    setLocale(nextLocale);

    const params = new URLSearchParams(window.location.search);
    const templateId = params.get("template");
    const pack = params.get("pack") as DecisionPack | null;
    const template = templateId ? decisionTemplateExamples[templateId] : null;
    const selectedTemplate = template ?? (pack && packExamples[pack] ? packExamples[pack] : null);
    if (selectedTemplate) {
      loadDecisionRequest(selectedTemplate);
    }
  }, []);

  function toggleLocale() {
    const next = locale === "en" ? "zh" : "en";
    setLocale(next);
    window.localStorage.setItem("decisionos.locale", next);
  }

  function applyPack(pack: DecisionPack) {
    setInputMode("template");
    loadDecisionRequest(packExamples[pack]);
  }

  function readFileAsBase64(file: File) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result;
        if (typeof result === "string") {
          resolve(result.split(",", 2)[1] ?? result);
        } else {
          reject(new Error("Unable to read file"));
        }
      };
      reader.onerror = () => reject(reader.error ?? new Error("Unable to read file"));
      reader.readAsDataURL(file);
    });
  }

  async function handleUploadParse() {
    if (!uploadFile) return;
    setUploadParsing(true);
    setError("");
    setUploadResult(null);
    try {
      const contentBase64 = await readFileAsBase64(uploadFile);
      const response = await fetchWithTimeout("/api/decision/parse-upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fileName: uploadFile.name,
          contentBase64,
          language: locale
        })
      });
      if (!response.ok) {
        throw new Error(await getResponseError(response));
      }
      const data = await response.json() as UploadParseResponse;
      loadDecisionRequest(data.parsed);
      setUploadResult(data);
      setInputMode("upload");
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      const isTimeout = err instanceof DOMException && err.name === "AbortError";
      setError(`${copy.errorPrefix}: ${isTimeout ? copy.errorTimeout : (message || copy.errorFallback)}`);
    } finally {
      setUploadParsing(false);
    }
  }

  async function handleParse() {
    if (!sentenceInput.trim()) return;
    setParsing(true);
    setError("");
    try {
      const res = await fetchWithTimeout("/api/decision/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sentence: sentenceInput.trim() })
      });
      if (!res.ok) throw new Error(await getResponseError(res));
      const data = await res.json();
      if (data.error) {
        setError(copy.parserError + ": " + data.error);
        return;
      }
      const p = data.parsed;
      const updated: DecisionRequest = {
        title: p.title || "",
        pack: p.pack || "Custom",
        context: p.context || "",
        objective: p.objective || "",
        options: Array.isArray(p.options) && p.options.length > 0 ? p.options : ["Option 1"],
        constraints: p.constraints || "",
        budget: typeof p.budget === "number" ? p.budget : 0,
        timeline: p.timeline || "",
        stakeholders: p.stakeholders || "",
        success_metrics: p.success_metrics || "",
        known_risks: p.known_risks || "",
      };
      loadDecisionRequest(updated);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "";
      setError(`${copy.parserError}: ${msg}`);
    } finally {
      setParsing(false);
    }
  }

  function loadDecisionRequest(next: DecisionRequest) {
    setForm(next);
    setOptionsText(next.options.join("\n"));
    setReport(null);
    setFollowUpSession(null);
    setFollowUpAnswers({});
    setFeedbackChanges([]);
    setFeedbackText("");
    setUploadResult(null);
    setError("");
  }

  function newDecision() {
    const next = { ...packExamples.Custom, title: "", context: "", objective: "", options: [] };
    setForm(next);
    setOptionsText("");
    setReport(null);
    setFollowUpSession(null);
    setFollowUpAnswers({});
    setFeedbackChanges([]);
    setFeedbackText("");
    setInputMode("manual");
    setUploadFile(null);
    setUploadResult(null);
    setError("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setReport(null);
    setFollowUpSession(null);
    setFollowUpAnswers({});
    setFeedbackChanges([]);
    setFeedbackText("");
    try {
      const response = await fetchWithTimeout("/api/decision/generate-followups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pack: form.pack,
          formData: { ...form, language: locale, options: splitOptions(optionsText) }
        })
      });
      if (!response.ok) {
        throw new Error(await getResponseError(response));
      }
      setFollowUpSession(await response.json());
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      const isTimeout = err instanceof DOMException && err.name === "AbortError";
      setError(`${copy.errorPrefix}: ${isTimeout ? copy.errorTimeout : (message || copy.errorFallback)}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleFollowUpSubmit() {
    if (!followUpSession) return;

    setFollowUpLoading(true);
    setError("");
    try {
      const answers = followUpSession.questions.map((question) => ({
        id: question.id,
        answer: followUpAnswers[question.id] ?? ""
      }));
      const contextResponse = await fetchWithTimeout("/api/decision/submit-answers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decisionId: followUpSession.decisionId, answers })
      });
      if (!contextResponse.ok) {
        throw new Error(await getResponseError(contextResponse));
      }
      const contextData = await contextResponse.json();
      const reportResponse = await fetchWithTimeout("/api/decision/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          language: locale,
          options: splitOptions(optionsText),
          context: contextData.combined_context
        })
      });
      if (!reportResponse.ok) {
        throw new Error(await getResponseError(reportResponse));
      }
      setReport(await reportResponse.json());
      setFollowUpSession({ ...followUpSession, status: "completed" });
      setFeedbackChanges([]);
      setFeedbackText("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      const isTimeout = err instanceof DOMException && err.name === "AbortError";
      setError(`${copy.errorPrefix}: ${isTimeout ? copy.errorTimeout : (message || copy.errorFallback)}`);
    } finally {
      setFollowUpLoading(false);
    }
  }

  async function handleFeedbackSubmit() {
    if (!report || !feedbackText.trim()) return;

    setFeedbackLoading(true);
    setError("");
    try {
      const response = await fetchWithTimeout("/api/decision/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decisionId: report.report_id, feedback: feedbackText })
      });
      if (!response.ok) {
        throw new Error(await getResponseError(response));
      }
      const data = await response.json();
      setReport(data.updatedReport);
      setFeedbackChanges(data.changes ?? []);
      setFeedbackText("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      const isTimeout = err instanceof DOMException && err.name === "AbortError";
      setError(`${copy.errorPrefix}: ${isTimeout ? copy.errorTimeout : (message || copy.errorFallback)}`);
    } finally {
      setFeedbackLoading(false);
    }
  }

  return (
    <main className="app-shell decision-shell">
      <TopNav
        icon={<BrainCircuit size={18} />}
        title="DecisionOS"
        locale={locale}
        actions={
          <>
            <button className="secondary-button language-toggle" type="button" onClick={toggleLocale}>
              {copy.language}
            </button>
            <button className="secondary-button" type="button" onClick={newDecision}>
              <Plus size={16} />
              {copy.navAction}
            </button>
          </>
        }
      />

      <section className="decision-hero">
        <div>
          <span className="eyebrow">{copy.eyebrow}</span>
          <h1>DecisionOS</h1>
          <p>{copy.hero}</p>
        </div>
        <div className="decision-hero-meta">
          {reportSectionKeys.slice(0, 5).map((key) => {
            const section = copy.reportSections[key];
            return <span key={section}>{section}</span>;
          })}
        </div>
      </section>

      <div className="decision-workspace">
        <section className="panel decision-inputs">
          <div className="panel-header">
            <h2 className="panel-title">{copy.inputsTitle}</h2>
            <p className="panel-subtitle">{copy.inputsSubtitle}</p>
          </div>

          <div className="input-mode-tabs">
            {(["manual", "template", "upload"] as InputMode[]).map((mode) => (
              <button className={inputMode === mode ? "active" : ""} key={mode} type="button" onClick={() => setInputMode(mode)}>
                {mode === "upload" ? <UploadCloud size={15} /> : mode === "template" ? <ClipboardList size={15} /> : <FileText size={15} />}
                {copy.inputModes[mode]}
              </button>
            ))}
          </div>

          {inputMode === "upload" ? (
            <div className="upload-plan-panel">
              <div>
                <strong>{copy.uploadTitle}</strong>
                <p>{copy.uploadBody}</p>
                <span>{copy.uploadFormats}</span>
              </div>
              <label className="upload-dropzone">
                <UploadCloud size={20} />
                <input
                  type="file"
                  accept=".txt,.md,.markdown,.docx,.pdf,text/plain,text/markdown,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
                />
                <b>{uploadFile?.name ?? copy.uploadTitle}</b>
              </label>
              <button className="secondary-button upload-parse-button" type="button" onClick={handleUploadParse} disabled={!uploadFile || uploadParsing}>
                {uploadParsing ? <Loader2 size={15} /> : <Sparkles size={15} />}
                {uploadParsing ? copy.uploadLoading : copy.uploadButton}
              </button>
              {uploadResult ? (
                <div className="upload-result">
                  <div>
                    <strong>{copy.uploadParsed}</strong>
                    <span>{copy.uploadConfidence}: {uploadResult.confidence}/100</span>
                  </div>
                  <p>{copy.uploadApplyHint}</p>
                  {uploadResult.field_sources?.length ? (
                    <div className="upload-field-sources">
                      <strong>{copy.uploadFieldSources}</strong>
                      {uploadResult.field_sources.map((field) => (
                        <article key={field.field}>
                          <div>
                            <b>{field.label}</b>
                            <span>{field.confidence}/100</span>
                          </div>
                          <p>{field.value}</p>
                          <small>{copy.uploadSource}: {field.source_excerpt}</small>
                        </article>
                      ))}
                    </div>
                  ) : null}
                  {uploadResult.warnings.map((warning) => (
                    <small key={warning}>{warning}</small>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}

          <div className="pack-grid">
            {packs.map((pack) => (
              <button className={pack.name === form.pack ? "pack-card active" : "pack-card"} key={pack.name} type="button" onClick={() => applyPack(pack.name)}>
                <strong>{pack.name}</strong>
                <span>{pack.description[locale]}</span>
              </button>
            ))}
          </div>

          <form className="form" onSubmit={handleSubmit}>
            <div className="parser-section">
              <label className="parser-label">{copy.parserLabel}</label>
              <div className="parser-row">
                <textarea
                  className="parser-input"
                  value={sentenceInput}
                  onChange={(e) => setSentenceInput(e.target.value)}
                  placeholder={copy.parserPlaceholder}
                  rows={2}
                />
                <button
                  className="parser-button"
                  type="button"
                  onClick={handleParse}
                  disabled={parsing || !sentenceInput.trim()}
                >
                  {parsing ? copy.parserLoading : copy.parserButton}
                </button>
              </div>
            </div>
            <div className="field">
              <label>{copy.titleLabel}</label>
              <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} placeholder={copy.titlePlaceholder} />
            </div>
            <div className="field">
              <label>{copy.packLabel}</label>
              <select value={form.pack} onChange={(event) => applyPack(event.target.value as DecisionPack)}>
                {packs.map((pack) => (
                  <option key={pack.name}>{pack.name}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>{copy.contextLabel}</label>
              <textarea value={form.context} onChange={(event) => setForm({ ...form, context: event.target.value })} />
            </div>
            <div className="field">
              <label>{copy.objectiveLabel}</label>
              <input value={form.objective} onChange={(event) => setForm({ ...form, objective: event.target.value })} />
            </div>
            <div className="field">
              <label>{copy.optionsLabel}</label>
              <textarea value={optionsText} onChange={(event) => setOptionsText(event.target.value)} />
            </div>
            <div className="decision-two-col">
              <div className="field">
                <label>{copy.budgetLabel}</label>
                <input type="number" value={form.budget} onChange={(event) => setForm({ ...form, budget: Number(event.target.value) })} />
              </div>
              <div className="field">
                <label>{copy.timelineLabel}</label>
                <input value={form.timeline} onChange={(event) => setForm({ ...form, timeline: event.target.value })} />
              </div>
            </div>
            <div className="field">
              <label>{copy.constraintsLabel}</label>
              <textarea value={form.constraints} onChange={(event) => setForm({ ...form, constraints: event.target.value })} />
            </div>
            <div className="field">
              <label>{copy.stakeholdersLabel}</label>
              <input value={form.stakeholders} onChange={(event) => setForm({ ...form, stakeholders: event.target.value })} />
            </div>
            <div className="field">
              <label>{copy.metricsLabel}</label>
              <textarea value={form.success_metrics} onChange={(event) => setForm({ ...form, success_metrics: event.target.value })} />
            </div>
            <div className="field">
              <label>{copy.risksLabel}</label>
              <textarea value={form.known_risks} onChange={(event) => setForm({ ...form, known_risks: event.target.value })} />
            </div>
            {error ? (
              <div className="error">
                <strong>{error}</strong>
                <span>{copy.errorHint}</span>
              </div>
            ) : null}
            <button className="submit" type="submit" disabled={loading}>
              {loading ? <Loader2 size={16} /> : <Sparkles size={16} />}
              {loading ? copy.loading : copy.submit}
            </button>
          </form>
        </section>

        <section className="panel decision-thinking">
          <div className="panel-header">
            <h2 className="panel-title">{copy.thinkingTitle}</h2>
            <p className="panel-subtitle">{selectedPack.name} {copy.lens}: {selectedPack.description[locale]}</p>
          </div>
          {followUpSession && !report ? (
            <FollowUpStep
              session={followUpSession}
              answers={followUpAnswers}
              loading={followUpLoading}
              locale={locale}
              onAnswerChange={(id, value) => setFollowUpAnswers((current) => ({ ...current, [id]: value }))}
              onSubmit={handleFollowUpSubmit}
              onCancel={() => {
                setFollowUpSession(null);
                setFollowUpAnswers({});
              }}
            />
          ) : (
            <div className="reasoning-list">
              {(report?.reasoning_timeline ?? copy.defaultSteps).map((step, index) => (
                <article className="reasoning-step" key={`${step.label}-${index}`}>
                  <div className="reasoning-index">{index + 1}</div>
                  <div>
                    <div className="reasoning-head">
                      <strong>{step.label}</strong>
                      <span>{step.status}</span>
                    </div>
                    <p>{step.focus}</p>
                    <small>{step.signal}</small>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="panel decision-report">
          <div className="panel-header">
            <h2 className="panel-title">{copy.reportTitle}</h2>
            <p className="panel-subtitle">{copy.reportSubtitle}</p>
          </div>
          {report ? (
            <ReportView
              report={report}
              locale={locale}
              feedbackText={feedbackText}
              feedbackLoading={feedbackLoading}
              feedbackChanges={feedbackChanges}
              onFeedbackChange={setFeedbackText}
              onFeedbackSubmit={handleFeedbackSubmit}
            />
          ) : (
            <EmptyReport locale={locale} />
          )}
        </section>
      </div>
    </main>
  );
}

function EmptyReport({ locale }: { locale: Locale }) {
  const copy = text[locale];
  return (
    <div className="decision-empty">
      <ClipboardList size={34} />
      <strong>{copy.emptyTitle}</strong>
      <p>{copy.emptyBody}</p>
      <div className="report-section-list">
        {reportSectionKeys.map((key) => {
          const section = copy.reportSections[key];
          return <span key={section}>{section}</span>;
        })}
      </div>
    </div>
  );
}

function ReportView({
  report,
  locale,
  feedbackText,
  feedbackLoading,
  feedbackChanges,
  onFeedbackChange,
  onFeedbackSubmit
}: {
  report: DecisionReport;
  locale: Locale;
  feedbackText: string;
  feedbackLoading: boolean;
  feedbackChanges: FeedbackChange[];
  onFeedbackChange: (value: string) => void;
  onFeedbackSubmit: () => void;
}) {
  const copy = text[locale];
  const [exportFormat, setExportFormat] = useState<"pdf" | "markdown">("pdf");
  const [copiedReport, setCopiedReport] = useState(false);
  const changedSections = new Set(feedbackChanges.map((change) => change.section));
  const blockClass = (section: string) => (changedSections.has(section) ? "changed" : undefined);
  const reportText = formatReportText(report);
  const verdictStrength = getVerdictStrength(report.scoring_summary.total_score, report.decision_verdict, locale);

  async function copyReportText() {
    await navigator.clipboard.writeText(reportText);
    setCopiedReport(true);
    window.setTimeout(() => setCopiedReport(false), 1500);
  }

  return (
    <div className="report-stack">
      <div className="report-export-bar">
        <div>
          <select value={exportFormat} onChange={(event) => setExportFormat(event.target.value as "pdf" | "markdown")}>
            <option value="pdf">{copy.exportPdf}</option>
            <option value="markdown">{copy.exportMarkdown}</option>
          </select>
          <a className="secondary-button" href={`/api/decision/${report.report_id}/export?format=${exportFormat}`}>
            <Download size={15} />
            {copy.exportLabel}
          </a>
        </div>
        <button className="secondary-button" type="button" onClick={copyReportText}>
          <Copy size={15} />
          {copiedReport ? copy.copiedReport : copy.copyReport}
        </button>
      </div>
      <ReportBlock title={copy.reportSections.executive_summary} className={blockClass("executive_summary")}>
        <p>{report.executive_summary}</p>
      </ReportBlock>
      <ReportBlock title={copy.reportSections.decision_verdict} className={blockClass("decision_verdict")}>
        <span className={`verdict-strength ${verdictStrength.className}`}>{verdictStrength.label}</span>
        <div className="verdict">
          <CheckCircle2 size={18} />
          <strong>{report.decision_verdict}</strong>
        </div>
      </ReportBlock>
      <ReportBlock title={copy.reportSections.scoring_engine} className={blockClass("scoring_summary")}>
        <div className="scoring-summary">
          <div className="score-total">
            <span>{report.scoring_summary.framework}</span>
            <strong>{report.scoring_summary.total_score}/100</strong>
            <p>{report.scoring_summary.recommendation}</p>
          </div>
          <div className="score-dimensions">
            {report.scoring_summary.dimensions.map((dimension) => (
              <article key={dimension.key}>
                <div>
                  <strong>{dimension.label}</strong>
                  <span>{Math.round(dimension.weight * 100)}%</span>
                </div>
                <meter min="0" max="100" value={dimension.score} />
                <p>{dimension.score}/100 · {dimension.reason}</p>
              </article>
            ))}
          </div>
        </div>
      </ReportBlock>
      <ReportBlock title={copy.reportSections.reference_cases} className={blockClass("reference_cases")}>
        <div className="reference-cases">
          {report.reference_cases.map((businessCase) => (
            <article key={businessCase.id}>
              <div>
                <strong>{businessCase.title}</strong>
                <span>{businessCase.similarity}%</span>
              </div>
              <small>
                {businessCase.company} · {businessCase.year} · {businessCase.pack}
              </small>
              <p>{businessCase.lesson}</p>
            </article>
          ))}
        </div>
      </ReportBlock>
      <ReportBlock title={copy.reportSections.core_value} className={blockClass("core_value")}>
        <BulletList items={report.core_value} />
      </ReportBlock>
      <ReportBlock title={copy.reportSections.benchmark} className={blockClass("benchmark")}>
        <BulletList items={report.benchmark} />
      </ReportBlock>
      <ReportBlock title={copy.reportSections.risk_matrix} className={blockClass("risk_matrix")}>
        <div className="risk-matrix">
          {report.risk_matrix.map((risk) => (
            <article key={risk.risk}>
              <div>
                <ShieldAlert size={15} />
                <strong>{risk.risk}</strong>
              </div>
              <span>{copy.likelihood}: {risk.likelihood}</span>
              <span>{copy.impact}: {risk.impact}</span>
              <p>{risk.mitigation}</p>
            </article>
          ))}
        </div>
      </ReportBlock>
      <ReportBlock title={copy.reportSections.execution_plan} className={blockClass("execution_plan")}>
        <NumberedList items={report.execution_plan} />
      </ReportBlock>
      <ReportBlock title={copy.reportSections.budget} className={blockClass("budget")}>
        <BulletList items={report.budget} />
      </ReportBlock>
      <ReportBlock title={copy.reportSections.timeline} className={blockClass("timeline")}>
        <div className="timeline-grid">
          {report.timeline.map((item) => (
            <article key={item.phase}>
              <strong>{item.phase}</strong>
              <span>{item.window}</span>
              <p>{item.output}</p>
            </article>
          ))}
        </div>
      </ReportBlock>
      <ReportBlock title={copy.reportSections.next_actions} className={blockClass("next_actions")}>
        <div className="next-actions">
          {report.next_actions.map((item) => (
            <div key={item}>
              <ArrowRight size={15} />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </ReportBlock>
      <ActionList items={report.action_items} locale={locale} />
      <ReportBlock title={copy.reportSections.feedback}>
        <div className="feedback-panel">
          {feedbackChanges.length ? (
            <div className="feedback-changes">
              <strong>{copy.feedbackChanges}</strong>
              {feedbackChanges.map((change) => (
                <article key={`${change.section}-${change.after}`}>
                  <span>{change.section}</span>
                  <p>{change.reason}</p>
                </article>
              ))}
            </div>
          ) : null}
          <textarea value={feedbackText} onChange={(event) => onFeedbackChange(event.target.value)} placeholder={copy.feedbackPlaceholder} />
          <button className="submit" type="button" onClick={onFeedbackSubmit} disabled={feedbackLoading || !feedbackText.trim()}>
            {feedbackLoading ? <Loader2 size={16} /> : <Sparkles size={16} />}
            {feedbackLoading ? copy.feedbackLoading : copy.feedbackSubmit}
          </button>
        </div>
      </ReportBlock>
    </div>
  );
}

function ReportBlock({ title, children, className }: { title: string; children: ReactNode; className?: string }) {
  return (
    <section className={className ? `report-block ${className}` : "report-block"}>
      <h3>{title}</h3>
      {children}
    </section>
  );
}

function BulletList({ items }: { items: string[] }) {
  return (
    <ul className="report-list">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function NumberedList({ items }: { items: string[] }) {
  return (
    <ol className="report-list numbered">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ol>
  );
}
