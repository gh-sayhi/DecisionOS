import { ArrowRight, BrainCircuit, FolderKanban, Plus } from "lucide-react";
import Link from "next/link";
import { TopNav } from "@/components/top-nav";

const decisionTemplates = [
  {
    id: "product-expansion",
    title: "产品扩展决策",
    pack: "Product",
    status: "模板已就绪",
    summary: "用于判断路线图投入优先级、发布范围和采用证据。"
  },
  {
    id: "market-entry",
    title: "市场进入决策",
    pack: "Startup",
    status: "模板已就绪",
    summary: "用于比较切入点、资金需求、进入速度和下行风险。"
  },
  {
    id: "capital-allocation",
    title: "资金配置决策",
    pack: "Investment",
    status: "模板已就绪",
    summary: "用于评估回报、流动性、战略匹配和风险控制。"
  }
];

export default function DecisionLibraryPage() {
  return (
    <main className="app-shell">
      <TopNav icon={<BrainCircuit size={18} />} title="DecisionOS" />
      <section className="project-workspace">
        <aside className="panel project-index">
          <div className="panel-header">
            <h1 className="panel-title">决策库</h1>
            <p className="panel-subtitle">面向管理层评审的可复用 Pack 和决策模板。</p>
          </div>
          <div className="project-index-list">
            {decisionTemplates.map((item) => (
              <Link className="project-index-card" href={`/?template=${item.id}`} key={item.title}>
                <strong>{item.title}</strong>
                <span>{item.pack} · {item.status}</span>
              </Link>
            ))}
          </div>
        </aside>
        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">决策模板</h2>
            <p className="panel-subtitle">每个模板都使用统一报告结构：摘要、结论、价值、对标、风险、计划、预算、时间线和下一步动作。</p>
          </div>
          <div className="report-stack">
            {decisionTemplates.map((item) => (
              <article className="report-block" key={item.title}>
                <h3>
                  <FolderKanban size={16} /> {item.title}
                </h3>
                <p>{item.summary}</p>
                <div className="next-actions">
                  <Link href={`/?template=${item.id}`}>
                    <ArrowRight size={15} />
                    <span>使用此模板进入 {item.pack} Pack。</span>
                  </Link>
                </div>
              </article>
            ))}
            <Link className="submit" href="/">
              <Plus size={16} />
              新建决策
            </Link>
          </div>
        </section>
      </section>
    </main>
  );
}
