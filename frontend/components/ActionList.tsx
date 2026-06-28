"use client";

import { CheckSquare, Copy } from "lucide-react";
import { useMemo, useState } from "react";
import type { ActionItem } from "@/lib/types";

type Locale = "en" | "zh";

type ActionListProps = {
  items: ActionItem[];
  locale: Locale;
};

const copy = {
  en: {
    title: "This Week Action List",
    subtitle: "Operational tasks generated from the decision report.",
    copy: "Copy actions",
    copied: "Copied",
    owner: "Owner",
    duration: "Duration"
  },
  zh: {
    title: "本周行动清单",
    subtitle: "根据决策报告自动生成的可执行任务。",
    copy: "复制清单",
    copied: "已复制",
    owner: "负责人",
    duration: "时长"
  }
};

function priorityClass(priority: string) {
  const normalized = priority.toLowerCase();
  if (normalized.includes("high") || priority.includes("高")) return "high";
  if (normalized.includes("low") || priority.includes("低")) return "low";
  return "medium";
}

export function ActionList({ items, locale }: ActionListProps) {
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [copied, setCopied] = useState(false);
  const text = copy[locale];

  const clipboardText = useMemo(
    () =>
      items
        .map((item) => `${item.day} | ${item.task} | ${text.owner}: ${item.owner} | ${text.duration}: ${item.duration} | ${item.priority}`)
        .join("\n"),
    [items, text.duration, text.owner]
  );

  async function copyActions() {
    await navigator.clipboard.writeText(clipboardText);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }

  return (
    <section className="action-list">
      <div className="action-list-head">
        <div>
          <span>
            <CheckSquare size={15} />
            {text.title}
          </span>
          <p>{text.subtitle}</p>
        </div>
        <button className="secondary-button" type="button" onClick={copyActions}>
          <Copy size={15} />
          {copied ? text.copied : text.copy}
        </button>
      </div>

      <div className="action-items">
        {items.map((item) => {
          const key = `${item.day}-${item.task}`;
          const isChecked = Boolean(checked[key]);
          return (
            <label className={`action-item${isChecked ? " checked" : ""}`} key={key}>
              <input type="checkbox" checked={isChecked} onChange={() => setChecked((current) => ({ ...current, [key]: !current[key] }))} />
              <div>
                <div className="action-item-main">
                  <strong>{item.day}</strong>
                  <span className={`priority-pill ${priorityClass(item.priority)}`}>{item.priority}</span>
                </div>
                <p>{item.task}</p>
                <small>
                  {text.owner}: {item.owner} · {text.duration}: {item.duration}
                </small>
              </div>
            </label>
          );
        })}
      </div>
    </section>
  );
}
