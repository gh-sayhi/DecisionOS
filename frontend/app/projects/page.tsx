"use client";

import { ArrowRight, BrainCircuit, CheckCircle2, FolderKanban, Plus } from "lucide-react";
import Link from "next/link";
import { TopNav } from "@/components/top-nav";
import { decisionTemplates } from "@/lib/decision-templates";

const packOrder = ["Product", "Startup", "Marketing", "Content", "Hiring", "Investment", "Custom"];

export default function DecisionLibraryPage() {
  return (
    <main className="app-shell decision-shell">
      <TopNav
        icon={<FolderKanban size={18} />}
        title="DecisionOS"
        locale="zh"
        actions={
          <Link className="secondary-button" href="/">
            <Plus size={16} />
            新建决策
          </Link>
        }
      />

      <section className="decision-hero project-library-hero">
        <div>
          <span className="eyebrow">Decision Library</span>
          <h1>决策库</h1>
          <p>从模板开始，而不是从空白表单开始。选择一个最接近当前业务问题的模板，系统会自动带入首页决策输入区。</p>
        </div>
        <div className="decision-hero-meta">
          {packOrder.map((pack) => (
            <span key={pack}>{pack}</span>
          ))}
        </div>
      </section>

      <section className="project-workspace decision-library-workspace">
        <div className="panel project-index">
          <div className="panel-header">
            <h2 className="panel-title">决策模板</h2>
            <p className="panel-subtitle">覆盖产品、创业、营销、内容、招聘、投资和自定义决策。</p>
          </div>
          <div className="decision-template-grid">
            {decisionTemplates.map((template) => (
              <Link className="project-index-card decision-template-card" href={template.directUrl} key={template.id}>
                <div>
                  <span className="template-pack">{template.pack}</span>
                  <strong>{template.title}</strong>
                </div>
                <p>{template.summary}</p>
                <small>{template.bestFor}</small>
                <span className="template-cta">
                  使用此模板
                  <ArrowRight size={15} />
                </span>
              </Link>
            ))}
          </div>
        </div>

        <aside className="panel decision-library-guide">
          <div className="panel-header">
            <h2 className="panel-title">怎么用</h2>
            <p className="panel-subtitle">点击模板后会进入 New Decision，表单自动预填。</p>
          </div>
          <div className="next-actions library-steps">
            <div>
              <CheckCircle2 size={15} />
              <span>选择最接近业务场景的 Pack 模板。</span>
            </div>
            <div>
              <CheckCircle2 size={15} />
              <span>进入首页后，把模板内容改成真实项目情况。</span>
            </div>
            <div>
              <CheckCircle2 size={15} />
              <span>点击生成，先回答追问，再查看决策报告。</span>
            </div>
            <div>
              <BrainCircuit size={15} />
              <span>生成后可导出 PDF / Markdown，也可继续反驳修订。</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
