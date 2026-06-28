"use client";

import { ReactNode, useState } from "react";

type ExpandableTextProps = {
  children: ReactNode;
  className?: string;
  lines?: 2 | 3 | 4;
};

export function ExpandableText({ children, className = "script-step", lines = 3 }: ExpandableTextProps) {
  const [expanded, setExpanded] = useState(false);
  const lineClass = lines === 2 ? "clamp-2" : lines === 4 ? "clamp-4" : "clamp-3";

  return (
    <div className="expandable-text">
      <div className={`${className} ${expanded ? "is-expanded" : lineClass}`}>{children}</div>
      <button className="text-toggle" onClick={() => setExpanded((value) => !value)} type="button">
        {expanded ? "收起" : "展开全文"}
      </button>
    </div>
  );
}
