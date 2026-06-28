"use client";

import { ArrowRight, BrainCircuit, CheckCircle2, ClipboardList, Copy, Download, Loader2, Plus, ShieldAlert, Sparkles } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { ActionList } from "@/components/ActionList";
import { FollowUpStep } from "@/components/FollowUpStep";
import { TopNav } from "@/components/top-nav";
import { decisionTemplateExamples } from "@/lib/decision-templates";
import type { DecisionPack, DecisionReport, DecisionRequest, FeedbackChange, FollowUpSession } from "@/lib/types";

type Locale = "en" | "zh";

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
    title: "Launch an AI workspace module for enterprise users",
    pack: "Product",
    context: "Enterprise users need a faster way to turn fragmented project inputs into decisions, but the team has limited engineering capacity this quarter.",
    objective: "Decide whether to ship the first workspace module now or wait for deeper integrations.",
    options: ["Ship a focused MVP", "Wait for full integrations", "Pilot with two design partners"],
    constraints: "Eight-week delivery window, limited backend capacity, sales team needs demo material.",
    budget: 180000,
    timeline: "8 weeks",
    stakeholders: "Product, engineering, sales, customer success",
    success_metrics: "Activation rate, weekly active teams, time-to-first-report, design partner conversion",
    known_risks: "Shipping too broad may weaken product quality and delay adoption proof."
  },
  Startup: {
    title: "Enter the mid-market operations software category",
    pack: "Startup",
    context: "The team sees repeated demand from mid-market operators, but the category has entrenched workflow incumbents.",
    objective: "Decide whether to build a vertical wedge before raising the next round.",
    options: ["Vertical wedge", "Horizontal platform", "Services-led validation"],
    constraints: "Six months runway before fundraising narrative must be clear.",
    budget: 320000,
    timeline: "12 weeks",
    stakeholders: "Founders, early customers, investors",
    success_metrics: "Qualified pipeline, paid pilots, implementation time, retention signal",
    known_risks: "The market may require more implementation support than the team can absorb."
  },
  Marketing: {
    title: "Choose the next enterprise acquisition motion",
    pack: "Marketing",
    context: "Inbound volume is stable but enterprise conversion is uneven across segments and channels.",
    objective: "Select the highest-leverage acquisition motion for the next planning cycle.",
    options: ["Account-based campaign", "Partner webinar series", "Executive thought leadership"],
    constraints: "Small team, limited media budget, need measurable pipeline within one quarter.",
    budget: 120000,
    timeline: "Quarter",
    stakeholders: "Marketing, sales, revenue operations",
    success_metrics: "Pipeline created, meeting rate, win rate, cost per opportunity",
    known_risks: "Brand activity may not convert without sales follow-up discipline."
  },
  Content: {
    title: "Validate a serialized content initiative for a professional audience",
    pack: "Content",
    context: "The team has a narrative concept, defined audience, estimated production budget, channel mix, release cadence, monetization model, talent roles, and a concise premise.",
    objective: "Decide whether to fund a small pilot before scaling into a repeatable content program.",
    options: ["Pilot three episodes", "Build a full season", "Pause and test audience demand first"],
    constraints: "Lean production team, fixed launch window, brand safety requirements.",
    budget: 90000,
    timeline: "6 weeks",
    stakeholders: "Content lead, growth lead, finance, brand owner",
    success_metrics: "Audience retention, qualified subscribers, production cost per asset, sponsor interest",
    known_risks: "Creative ambition may exceed production capacity and weaken release consistency."
  },
  Hiring: {
    title: "Decide whether to hire a senior platform lead",
    pack: "Hiring",
    context: "Engineering throughput is constrained by architecture decisions, but the company is also watching burn closely.",
    objective: "Decide whether to hire full-time, contract, or redesign responsibilities internally.",
    options: ["Hire senior lead", "Use fractional advisor", "Promote internal owner"],
    constraints: "Budget sensitivity, urgent architecture work, limited interview bandwidth.",
    budget: 260000,
    timeline: "10 weeks",
    stakeholders: "CEO, CTO, engineering managers, finance",
    success_metrics: "Architecture decision velocity, team throughput, retention risk reduction",
    known_risks: "Hiring too senior may add cost before the operating model is ready."
  },
  Investment: {
    title: "Allocate capital to a new strategic asset",
    pack: "Investment",
    context: "The asset could strengthen long-term positioning, but short-term liquidity and downside exposure need clearer boundaries.",
    objective: "Decide whether to invest now, stage the investment, or wait.",
    options: ["Invest now", "Stage commitment", "Wait for better entry conditions"],
    constraints: "Liquidity target, board approval, uncertain macro conditions.",
    budget: 500000,
    timeline: "30 days",
    stakeholders: "Finance, strategy, board, operating owner",
    success_metrics: "Risk-adjusted return, strategic leverage, liquidity impact, downside protection",
    known_risks: "Opportunity cost may be high if market conditions deteriorate."
  },
  Custom: {
    title: "Resolve a strategic operating decision",
    pack: "Custom",
    context: "A leadership team needs a structured recommendation before committing budget, people, and executive attention.",
    objective: "Turn the open question into a clear verdict, operating plan, and next actions.",
    options: ["Proceed", "Revise", "Pause"],
    constraints: "Limited resources and incomplete evidence.",
    budget: 100000,
    timeline: "4 weeks",
    stakeholders: "Executive owner, finance, operators, end users",
    success_metrics: "Decision speed, quality of evidence, execution readiness, risk reduction",
    known_risks: "The decision may be delayed if ownership is unclear."
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
    inputsSubtitle: "Select a pack, define the business question, and provide enough evidence for a structured recommendation.",
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
    likelihood: "发生概率",
    impact: "影响程度",
    defaultSteps: [
      { label: "背景", focus: "等待决策背景", signal: "尚未生成报告", status: "就绪" },
      { label: "目标", focus: "映射业务结果", signal: "定义目标状态", status: "就绪" },
      { label: "选项", focus: "比较可行路径", signal: "添加备选方案", status: "就绪" },
      { label: "风险", focus: "识别约束和风险敞口", signal: "预算、时间、相关方、未知项", status: "就绪" },
      { label: "结论", focus: "把推理转成行动", signal: "生成报告", status: "就绪" }
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
    loadDecisionRequest(packExamples[pack]);
  }

  function loadDecisionRequest(next: DecisionRequest) {
    setForm(next);
    setOptionsText(next.options.join("\n"));
    setReport(null);
    setFollowUpSession(null);
    setFollowUpAnswers({});
    setFeedbackChanges([]);
    setFeedbackText("");
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
      const response = await fetch("/api/decision/generate-followups", {
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
      setError(`${copy.errorPrefix}: ${message || copy.errorFallback}`);
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
      const contextResponse = await fetch("/api/decision/submit-answers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decisionId: followUpSession.decisionId, answers })
      });
      if (!contextResponse.ok) {
        throw new Error(await getResponseError(contextResponse));
      }
      const contextData = await contextResponse.json();
      const reportResponse = await fetch("/api/decision/generate", {
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
      setError(`${copy.errorPrefix}: ${message || copy.errorFallback}`);
    } finally {
      setFollowUpLoading(false);
    }
  }

  async function handleFeedbackSubmit() {
    if (!report || !feedbackText.trim()) return;

    setFeedbackLoading(true);
    setError("");
    try {
      const response = await fetch("/api/decision/feedback", {
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
      setError(`${copy.errorPrefix}: ${message || copy.errorFallback}`);
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

          <div className="pack-grid">
            {packs.map((pack) => (
              <button className={pack.name === form.pack ? "pack-card active" : "pack-card"} key={pack.name} type="button" onClick={() => applyPack(pack.name)}>
                <strong>{pack.name}</strong>
                <span>{pack.description[locale]}</span>
              </button>
            ))}
          </div>

          <form className="form" onSubmit={handleSubmit}>
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
