"use client";

import { BarChart3, BrainCircuit, FolderKanban, Plus, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

type TopNavProps = {
  title?: string;
  icon?: ReactNode;
  actions?: ReactNode;
  locale?: "en" | "zh";
};

const navItems = [
  { href: "/", label: { en: "New Decision", zh: "新建决策" }, icon: Plus },
  { href: "/projects", label: { en: "Decision Library", zh: "决策库" }, icon: FolderKanban },
  { href: "/admin/login", label: { en: "Admin", zh: "管理后台" }, icon: Settings },
  { href: "http://127.0.0.1:8001/docs", label: { en: "API", zh: "API" }, icon: BarChart3, external: true }
];

export function TopNav({ title = "DecisionOS", icon, actions, locale = "zh" }: TopNavProps) {
  const pathname = usePathname();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <Link className="brand-mark" href="/">
          <span className="brand-icon">{icon || <BrainCircuit size={18} />}</span>
          <span>{title}</span>
        </Link>
        <nav className="top-menu" aria-label="主菜单">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = !item.external && (pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href)));
            const className = active ? "top-menu-link active" : "top-menu-link";
            if (item.external) {
              return (
                <a className={className} href={item.href} key={item.href} target="_blank" rel="noreferrer">
                  <Icon size={15} />
                  {item.label[locale]}
                </a>
              );
            }
            return (
              <Link className={className} href={item.href} key={item.href}>
                <Icon size={15} />
                {item.label[locale]}
              </Link>
            );
          })}
        </nav>
      </div>
      {actions ? <div className="topbar-actions">{actions}</div> : null}
    </header>
  );
}
