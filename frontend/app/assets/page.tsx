"use client";

import { Archive, CheckCircle2, ClipboardList, RefreshCcw } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { TopNav } from "@/components/top-nav";
import type { DecisionAsset, DecisionReview } from "@/lib/types";

type ReviewForm = {
  review_window: "7d" | "30d" | "90d";
  actual_outcome: string;
  metric_result: string;
  budget_result: string;
  risk_result: string;
  next_decision: string;
};

const emptyReview: ReviewForm = {
  review_window: "7d",
  actual_outcome: "",
  metric_result: "",
  budget_result: "",
  risk_result: "",
  next_decision: ""
};

export default function DecisionAssetsPage() {
  const [assets, setAssets] = useState<DecisionAsset[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [review, setReview] = useState<ReviewForm>(emptyReview);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const selected = useMemo(() => assets.find((item) => item.id === selectedId) ?? assets[0], [assets, selectedId]);
  const focusAssets = assets.filter((item) => item.pack === "Product" || item.pack === "Investment").length;

  useEffect(() => {
    loadAssets();
  }, []);

  async function loadAssets() {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/decision/assets", { cache: "no-store" });
      if (!response.ok) throw new Error("无法读取决策资产库");
      const data = await response.json();
      setAssets(data.assets ?? []);
      setSelectedId((data.assets?.[0]?.id as string | undefined) ?? "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "读取失败");
    } finally {
      setLoading(false);
    }
  }

  async function submitReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setSaving(true);
    setError("");
    try {
      const response = await fetch(`/api/decision/assets/${selected.id}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(review)
      });
      if (!response.ok) throw new Error("复盘保存失败");
      const saved = await response.json();
      setAssets((current) => current.map((item) => (item.id === saved.id ? saved : item)));
      setReview(emptyReview);
    } catch (err) {
      setError(err instanceof Error ? err.message : "复盘保存失败");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="app-shell decision-shell">
      <TopNav icon={<Archive size={18} />} title="DecisionOS" locale="zh" />

      <section className="decision-hero">
        <div>
          <span className="eyebrow">Decision Assets</span>
          <h1>决策资产库</h1>
          <p>每次生成的报告都会进入资产库。这里用于沉淀历史判断、实际结果和 7/30/90 天复盘，让 DecisionOS 从一次性工具变成组织决策系统。</p>
        </div>
        <div className="decision-hero-meta">
          <span>历史决策 {assets.length}</span>
          <span>主打 Pack {focusAssets}</span>
          <span>复盘记录 {assets.reduce((sum, item) => sum + item.reviews.length, 0)}</span>
        </div>
      </section>

      <section className="decision-assets-workspace">
        <aside className="panel asset-list-panel">
          <div className="panel-header">
            <h2 className="panel-title">历史决策</h2>
            <p className="panel-subtitle">优先沉淀 Product / Investment，其他 Pack 继续保留。</p>
          </div>
          {loading ? <div className="project-empty">加载中...</div> : null}
          {error ? <div className="error"><strong>{error}</strong><span>请确认 8001 后端服务已启动。</span></div> : null}
          {!loading && !assets.length ? (
            <div className="project-empty">暂无历史决策。先在首页生成一份报告。</div>
          ) : (
            <div className="asset-list">
              {assets.map((asset) => (
                <button className={asset.id === selected?.id ? "asset-card active" : "asset-card"} key={asset.id} type="button" onClick={() => setSelectedId(asset.id)}>
                  <span>{asset.pack}</span>
                  <strong>{asset.title}</strong>
                  <small>{asset.verdict_strength} · {asset.score}/100 · {asset.review_status}</small>
                </button>
              ))}
            </div>
          )}
        </aside>

        <section className="panel asset-detail-panel">
          {selected ? (
            <>
              <div className="panel-header">
                <h2 className="panel-title">{selected.title}</h2>
                <p className="panel-subtitle">{selected.pack} · {selected.report_id} · {new Date(selected.created_at).toLocaleString("zh-CN")}</p>
              </div>
              <div className="asset-kpi-grid">
                <div><span>评分</span><strong>{selected.score}/100</strong></div>
                <div><span>结论强弱</span><strong>{selected.verdict_strength}</strong></div>
                <div><span>复盘状态</span><strong>{selected.review_status}</strong></div>
              </div>
              <div className="asset-summary">
                <h3>原始结论</h3>
                <p>{selected.decision_verdict}</p>
                <h3>下一步动作</h3>
                <ul>
                  {selected.next_actions.slice(0, 5).map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>

              <div className="asset-review-grid">
                <div>
                  <h3><RefreshCcw size={16} /> 添加复盘</h3>
                  <form className="asset-review-form" onSubmit={submitReview}>
                    <label>
                      复盘窗口
                      <select value={review.review_window} onChange={(event) => setReview({ ...review, review_window: event.target.value as ReviewForm["review_window"] })}>
                        <option value="7d">7 天</option>
                        <option value="30d">30 天</option>
                        <option value="90d">90 天</option>
                      </select>
                    </label>
                    <label>
                      实际结果
                      <textarea value={review.actual_outcome} onChange={(event) => setReview({ ...review, actual_outcome: event.target.value })} required />
                    </label>
                    <label>
                      指标结果
                      <input value={review.metric_result} onChange={(event) => setReview({ ...review, metric_result: event.target.value })} placeholder="例如：激活率 18%，预算未超支" />
                    </label>
                    <label>
                      预算结果
                      <input value={review.budget_result} onChange={(event) => setReview({ ...review, budget_result: event.target.value })} />
                    </label>
                    <label>
                      风险结果
                      <textarea value={review.risk_result} onChange={(event) => setReview({ ...review, risk_result: event.target.value })} />
                    </label>
                    <label>
                      下一次决策
                      <input value={review.next_decision} onChange={(event) => setReview({ ...review, next_decision: event.target.value })} />
                    </label>
                    <button className="submit" type="submit" disabled={saving}>
                      {saving ? "保存中" : "保存复盘"}
                    </button>
                  </form>
                </div>
                <div>
                  <h3><ClipboardList size={16} /> 复盘记录</h3>
                  {selected.reviews.length ? (
                    <div className="review-list">
                      {selected.reviews.map((item: DecisionReview) => (
                        <article key={item.id}>
                          <strong>{item.review_window} · {new Date(item.created_at).toLocaleString("zh-CN")}</strong>
                          <p>{item.actual_outcome}</p>
                          <small>{item.metric_result || "未填写指标"} · {item.next_decision || "未填写下一次决策"}</small>
                        </article>
                      ))}
                    </div>
                  ) : (
                    <div className="project-empty">还没有复盘记录。建议生成报告后 7 天先做第一次复盘。</div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="decision-empty">
              <CheckCircle2 size={32} />
              <strong>等待决策资产</strong>
              <p>在首页生成报告后，这里会自动出现历史决策。</p>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
