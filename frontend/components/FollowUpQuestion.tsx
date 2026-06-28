"use client";

import type { FollowUpQuestion as FollowUpQuestionType } from "@/lib/types";

type FollowUpQuestionProps = {
  question: FollowUpQuestionType;
  value: string;
  onChange: (value: string) => void;
};

export function FollowUpQuestion({ question, value, onChange }: FollowUpQuestionProps) {
  if (question.type === "select") {
    return (
      <label className="followup-question">
        <span>{question.question}</span>
        <small>{question.context}</small>
        <select value={value} onChange={(event) => onChange(event.target.value)}>
          <option value="">Select an answer</option>
          {(question.options ?? []).map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
    );
  }

  if (question.type === "multiselect") {
    const selected = value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    return (
      <fieldset className="followup-question followup-choice-group">
        <legend>{question.question}</legend>
        <small>{question.context}</small>
        <div>
          {(question.options ?? []).map((option) => {
            const checked = selected.includes(option);
            return (
              <label key={option}>
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => {
                    const next = checked ? selected.filter((item) => item !== option) : [...selected, option];
                    onChange(next.join(", "));
                  }}
                />
                <span>{option}</span>
              </label>
            );
          })}
        </div>
      </fieldset>
    );
  }

  return (
    <label className="followup-question">
      <span>{question.question}</span>
      <small>{question.context}</small>
      {question.type === "textarea" ? (
        <textarea value={value} onChange={(event) => onChange(event.target.value)} />
      ) : (
        <input value={value} onChange={(event) => onChange(event.target.value)} />
      )}
    </label>
  );
}
