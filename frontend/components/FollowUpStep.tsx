"use client";

import { ArrowLeft, Loader2, Send } from "lucide-react";
import type { FollowUpSession } from "@/lib/types";
import { FollowUpQuestion } from "@/components/FollowUpQuestion";

type Locale = "en" | "zh";

type FollowUpStepProps = {
  session: FollowUpSession;
  answers: Record<string, string>;
  loading: boolean;
  locale: Locale;
  onAnswerChange: (id: string, value: string) => void;
  onSubmit: () => void;
  onCancel: () => void;
};

const copy = {
  en: {
    eyebrow: "Follow-up questions",
    title: "DecisionOS needs a little more context",
    body: "Answer these pack-specific questions before the report is generated.",
    progress: "answered",
    back: "Back to inputs",
    submit: "Generate report",
    loading: "Generating"
  },
  zh: {
    eyebrow: "追问问题",
    title: "DecisionOS 需要补充关键上下文",
    body: "请先回答这些与 Pack 相关的问题，系统再生成完整决策报告。",
    progress: "已回答",
    back: "返回输入",
    submit: "生成报告",
    loading: "生成中"
  }
};

export function FollowUpStep({ session, answers, loading, locale, onAnswerChange, onSubmit, onCancel }: FollowUpStepProps) {
  const answeredCount = session.questions.filter((question) => answers[question.id]?.trim()).length;
  const canSubmit = answeredCount === session.questions.length && !loading;
  const text = copy[locale];

  return (
    <div className="followup-step">
      <div className="followup-step-header">
        <span>{text.eyebrow}</span>
        <strong>{text.title}</strong>
        <p>{text.body}</p>
        <div className="followup-progress">
          <span>
            {answeredCount}/{session.questions.length} {text.progress}
          </span>
        </div>
      </div>

      <div className="followup-question-list">
        {session.questions.map((question, index) => (
          <article className="followup-card" key={question.id}>
            <div className="followup-number">{index + 1}</div>
            <FollowUpQuestion question={question} value={answers[question.id] ?? ""} onChange={(value) => onAnswerChange(question.id, value)} />
          </article>
        ))}
      </div>

      <div className="followup-actions">
        <button className="secondary-button" type="button" onClick={onCancel} disabled={loading}>
          <ArrowLeft size={15} />
          {text.back}
        </button>
        <button className="submit" type="button" onClick={onSubmit} disabled={!canSubmit}>
          {loading ? <Loader2 size={16} /> : <Send size={16} />}
          {loading ? text.loading : text.submit}
        </button>
      </div>
    </div>
  );
}
