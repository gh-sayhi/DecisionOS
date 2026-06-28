"use client";

import { Activity, BarChart3, Clapperboard, Download, Edit3, Eye, FileText, FolderKanban, LogOut, Plus, RefreshCw, Save, ScrollText, Trash2, Users } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { TopNav } from "@/components/top-nav";
import type { Actor, ActorInput, AdminSummary, CampaignReport, Creator, CreatorInput, DramaReport, LogEntry, ProjectRecord, ReportFile } from "@/lib/types";

const blankCreator: CreatorInput = {
  name: "",
  platform: "douyin",
  tags: [],
  followers: 0,
  conversion_rate: 0.03,
  avg_cpm: 60,
  risk_flags: []
};

const blankActor: ActorInput = {
  name: "",
  gender: "female",
  age_range: "22-28",
  location: "横店",
  image_tags: [],
  role_tags: [],
  genres: [],
  fee_min: 20000,
  fee_max: 50000,
  schedule_status: "available",
  followers: 0,
  completion_rate: 0.35,
  paid_conversion_rate: 0.03,
  past_works: [],
  risk_flags: []
};

function authHeaders(token: string) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`
  };
}

function splitCsv(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinCsv(value: string[]) {
  return value.join(", ");
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("zh-CN").format(value);
}

function formatDate(seconds: string) {
  const date = new Date(Number(seconds) * 1000);
  return Number.isNaN(date.getTime()) ? "-" : date.toLocaleString("zh-CN");
}

function formatIsoDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "-" : date.toLocaleString("zh-CN");
}

function projectKindLabel(kind: string) {
  return kind === "drama" ? "Content Decision" : "Business Decision";
}

const adminMenuItems = [
  { href: "/admin", key: "overview", label: "概览", icon: BarChart3 },
  { href: "/admin/projects", key: "projects", label: "项目库", icon: FolderKanban },
  { href: "/admin/creators", key: "creators", label: "Creator Pool", icon: Users },
  { href: "/admin/actors", key: "actors", label: "Talent Pool", icon: Clapperboard },
  { href: "/admin/reports", key: "reports", label: "报告列表", icon: FileText },
  { href: "/admin/logs", key: "logs", label: "日志管理", icon: ScrollText }
];

export default function AdminPage() {
  const router = useRouter();
  const pathname = usePathname();
  // 后台子页面复用同一个组件，根据 URL 的第三段决定当前显示哪个模块。
  const activeSection = pathname.split("/")[2] || "overview";
  const [token, setToken] = useState("");
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [creators, setCreators] = useState<Creator[]>([]);
  const [actors, setActors] = useState<Actor[]>([]);
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [reports, setReports] = useState<ReportFile[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [logLevel, setLogLevel] = useState("");
  const [logEvent, setLogEvent] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingActorId, setEditingActorId] = useState<string | null>(null);
  const [form, setForm] = useState<CreatorInput>(blankCreator);
  const [actorForm, setActorForm] = useState<ActorInput>(blankActor);
  const [tagText, setTagText] = useState("");
  const [riskText, setRiskText] = useState("");
  const [actorImageText, setActorImageText] = useState("");
  const [actorRoleText, setActorRoleText] = useState("");
  const [actorGenreText, setActorGenreText] = useState("");
  const [actorWorksText, setActorWorksText] = useState("");
  const [actorRiskText, setActorRiskText] = useState("");
  const [error, setError] = useState("");

  const editingCreator = useMemo(
    () => creators.find((creator) => creator.id === editingId) || null,
    [creators, editingId]
  );

  const editingActor = useMemo(
    () => actors.find((actor) => actor.id === editingActorId) || null,
    [actors, editingActorId]
  );

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId) || projects[0] || null,
    [projects, selectedProjectId]
  );

  // 项目库里保存的是完整报告快照，这里按项目类型还原成对应展示数据。
  const selectedDramaReport = selectedProject?.kind === "drama" ? (selectedProject.report as unknown as DramaReport) : null;
  const selectedCampaignReport = selectedProject?.kind === "brand" ? (selectedProject.report as unknown as CampaignReport) : null;

  async function loadAdminData(currentToken: string) {
    const [summaryResponse, creatorsResponse, actorsResponse, projectsResponse, reportsResponse, logsResponse] = await Promise.all([
      fetch("/api/admin/summary", { headers: authHeaders(currentToken) }),
      fetch("/api/admin/creators", { headers: authHeaders(currentToken) }),
      fetch("/api/admin/actors", { headers: authHeaders(currentToken) }),
      fetch("/api/admin/projects", { headers: authHeaders(currentToken) }),
      fetch("/api/admin/reports", { headers: authHeaders(currentToken) }),
      fetch("/api/admin/logs?limit=200", { headers: authHeaders(currentToken) })
    ]);
    if (!summaryResponse.ok || !creatorsResponse.ok || !actorsResponse.ok || !projectsResponse.ok || !reportsResponse.ok || !logsResponse.ok) {
      localStorage.removeItem("admin_token");
      router.push("/admin/login");
      return;
    }
    setSummary(await summaryResponse.json());
    setCreators(await creatorsResponse.json());
    setActors(await actorsResponse.json());
    const nextProjects: ProjectRecord[] = await projectsResponse.json();
    setProjects(nextProjects);
    setSelectedProjectId((current) => current || nextProjects[0]?.id || null);
    setReports(await reportsResponse.json());
    setLogs(await logsResponse.json());
  }

  async function loadLogs(currentToken = token) {
    const params = new URLSearchParams({ limit: "200" });
    if (logLevel) params.set("level", logLevel);
    if (logEvent) params.set("event", logEvent);
    const response = await fetch(`/api/admin/logs?${params.toString()}`, {
      headers: authHeaders(currentToken)
    });
    if (response.ok) {
      setLogs(await response.json());
    }
  }

  useEffect(() => {
    const saved = localStorage.getItem("admin_token");
    if (!saved) {
      router.push("/admin/login");
      return;
    }
    setToken(saved);
    loadAdminData(saved).catch(() => {
      localStorage.removeItem("admin_token");
      router.push("/admin/login");
    });
  }, [router]);

  function startEdit(creator: Creator) {
    setEditingId(creator.id);
    setForm({
      name: creator.name,
      platform: creator.platform,
      tags: creator.tags,
      followers: creator.followers,
      conversion_rate: creator.conversion_rate,
      avg_cpm: creator.avg_cpm,
      risk_flags: creator.risk_flags
    });
    setTagText(joinCsv(creator.tags));
    setRiskText(joinCsv(creator.risk_flags));
  }

  function startCreate() {
    setEditingId(null);
    setForm(blankCreator);
    setTagText("");
    setRiskText("");
  }

  function startActorEdit(actor: Actor) {
    setEditingActorId(actor.id);
    setActorForm({
      name: actor.name,
      gender: actor.gender,
      age_range: actor.age_range,
      location: actor.location,
      image_tags: actor.image_tags,
      role_tags: actor.role_tags,
      genres: actor.genres,
      fee_min: actor.fee_min,
      fee_max: actor.fee_max,
      schedule_status: actor.schedule_status,
      followers: actor.followers,
      completion_rate: actor.completion_rate,
      paid_conversion_rate: actor.paid_conversion_rate,
      past_works: actor.past_works,
      risk_flags: actor.risk_flags
    });
    setActorImageText(joinCsv(actor.image_tags));
    setActorRoleText(joinCsv(actor.role_tags));
    setActorGenreText(joinCsv(actor.genres));
    setActorWorksText(joinCsv(actor.past_works));
    setActorRiskText(joinCsv(actor.risk_flags));
  }

  function startActorCreate() {
    setEditingActorId(null);
    setActorForm(blankActor);
    setActorImageText("");
    setActorRoleText("");
    setActorGenreText("");
    setActorWorksText("");
    setActorRiskText("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const payload = {
      ...form,
      tags: splitCsv(tagText),
      risk_flags: splitCsv(riskText)
    };
    const url = editingId ? `/api/admin/creators/${editingId}` : "/api/admin/creators";
    const response = await fetch(url, {
      method: editingId ? "PUT" : "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      setError("保存失败，请检查字段。");
      return;
    }
    startCreate();
    await loadAdminData(token);
  }

  async function removeCreator(creatorId: string) {
    const response = await fetch(`/api/admin/creators/${creatorId}`, {
      method: "DELETE",
      headers: authHeaders(token)
    });
    if (response.ok) {
      await loadAdminData(token);
    }
  }

  async function handleActorSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const payload = {
      ...actorForm,
      image_tags: splitCsv(actorImageText),
      role_tags: splitCsv(actorRoleText),
      genres: splitCsv(actorGenreText),
      past_works: splitCsv(actorWorksText),
      risk_flags: splitCsv(actorRiskText)
    };
    const url = editingActorId ? `/api/admin/actors/${editingActorId}` : "/api/admin/actors";
    const response = await fetch(url, {
      method: editingActorId ? "PUT" : "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      setError("演员保存失败，请检查字段。");
      return;
    }
    startActorCreate();
    await loadAdminData(token);
  }

  async function removeActor(actorId: string) {
    const response = await fetch(`/api/admin/actors/${actorId}`, {
      method: "DELETE",
      headers: authHeaders(token)
    });
    if (response.ok) {
      await loadAdminData(token);
    }
  }

  function logout() {
    localStorage.removeItem("admin_token");
    router.push("/admin/login");
  }

  async function clearActivityLogs() {
    const response = await fetch("/api/admin/logs", {
      method: "DELETE",
      headers: authHeaders(token)
    });
    if (response.ok) {
      await loadAdminData(token);
    }
  }

  return (
    <main className="app-shell">
      <TopNav
        title="管理后台"
        icon={<Users size={18} />}
        actions={
          <button className="button-secondary" onClick={logout} type="button">
            <LogOut size={16} />
            退出
          </button>
        }
      />

      <div className="admin-shell">
        {/* 左侧菜单只负责路由跳转，每个路由仍共享同一套数据加载和鉴权逻辑。 */}
        <aside className="admin-sidebar">
          <nav className="admin-side-menu" aria-label="后台菜单">
            {adminMenuItems.map((item) => {
              const Icon = item.icon;
              const active = activeSection === item.key;
              return (
                <Link className={active ? "admin-side-link active" : "admin-side-link"} href={item.href} key={item.key}>
                  <Icon size={16} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>

        <div className="admin-layout">
        {activeSection === "overview" ? <section className="panel">
          <div className="metric-grid">
            <div className="metric">
              <div className="metric-label">达人数量</div>
              <div className="metric-value">{summary ? formatNumber(summary.creators) : "-"}</div>
            </div>
            <div className="metric">
              <div className="metric-label">报告数量</div>
              <div className="metric-value">{summary ? formatNumber(summary.reports) : "-"}</div>
            </div>
            <div className="metric">
              <div className="metric-label">项目数量</div>
              <div className="metric-value">{summary ? formatNumber(summary.projects) : "-"}</div>
            </div>
            <div className="metric">
              <div className="metric-label">演员数量</div>
              <div className="metric-value">{summary ? formatNumber(summary.actors) : "-"}</div>
            </div>
            <div className="metric">
              <div className="metric-label">日志数量</div>
              <div className="metric-value">{summary ? formatNumber(summary.logs) : "-"}</div>
            </div>
          </div>
        </section> : null}

        {activeSection === "creators" ? <div className="admin-grid">
          <section className="panel">
            <div className="toolbar">
              <div>
                <h1 className="panel-title">Creator Pool</h1>
                <p className="panel-subtitle">Manage local JSON resource data used by matching and recommendation workflows.</p>
              </div>
              <button className="button-secondary" onClick={startCreate} type="button">
                <Plus size={16} />
                新建
              </button>
            </div>
            <div className="section">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>达人</th>
                    <th>平台</th>
                    <th>粉丝</th>
                    <th>转化</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {creators.map((creator) => (
                    <tr key={creator.id}>
                      <td>
                        <strong>{creator.name}</strong>
                        <div className="creator-meta">{creator.tags.join(", ")}</div>
                      </td>
                      <td>{creator.platform}</td>
                      <td>{formatNumber(creator.followers)}</td>
                      <td>{(creator.conversion_rate * 100).toFixed(1)}%</td>
                      <td>
                        <div className="compact-actions">
                          <button className="button-secondary" onClick={() => startEdit(creator)} type="button">
                            <Edit3 size={14} />
                            编辑
                          </button>
                          <button className="button-danger" onClick={() => removeCreator(creator.id)} type="button">
                            <Trash2 size={14} />
                            删除
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h2 className="panel-title">{editingId ? "编辑达人" : "新建达人"}</h2>
              <p className="panel-subtitle">标签和风险项用英文逗号分隔。</p>
            </div>
            <form className="admin-form" onSubmit={handleSubmit}>
              <div className="field">
                <label>名称</label>
                <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
              </div>
              <div className="field">
                <label>平台</label>
                <select value={form.platform} onChange={(event) => setForm({ ...form, platform: event.target.value })}>
                  <option value="douyin">抖音</option>
                  <option value="xiaohongshu">小红书</option>
                  <option value="bilibili">B站</option>
                </select>
              </div>
              <div className="field">
                <label>粉丝数</label>
                <input
                  type="number"
                  value={form.followers}
                  onChange={(event) => setForm({ ...form, followers: Number(event.target.value) })}
                />
              </div>
              <div className="field">
                <label>转化率</label>
                <input
                  type="number"
                  step="0.001"
                  value={form.conversion_rate}
                  onChange={(event) => setForm({ ...form, conversion_rate: Number(event.target.value) })}
                />
              </div>
              <div className="field">
                <label>平均 CPM</label>
                <input
                  type="number"
                  value={form.avg_cpm}
                  onChange={(event) => setForm({ ...form, avg_cpm: Number(event.target.value) })}
                />
              </div>
              <div className="field">
                <label>标签</label>
                <input value={tagText} onChange={(event) => setTagText(event.target.value)} />
              </div>
              <div className="field">
                <label>风险项</label>
                <input value={riskText} onChange={(event) => setRiskText(event.target.value)} />
              </div>
              {error ? <div className="error">{error}</div> : null}
              <button className="submit" type="submit">
                <Save size={16} />
                保存
              </button>
            </form>
          </section>
        </div> : null}

        {activeSection === "actors" ? <div className="admin-grid">
          <section className="panel">
            <div className="toolbar">
              <div>
                <h2 className="panel-title">Talent Pool</h2>
                <p className="panel-subtitle">Manage people, capability tags, availability and cost assumptions for decision support.</p>
              </div>
              <button className="button-secondary" onClick={startActorCreate} type="button">
                <Plus size={16} />
                新建
              </button>
            </div>
            <div className="section">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Talent</th>
                    <th>Capability Tags</th>
                    <th>Cost Range</th>
                    <th>档期</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {actors.map((actor) => (
                    <tr key={actor.id}>
                      <td>
                        <strong>{actor.name}</strong>
                        <div className="creator-meta">
                          {actor.gender} | {actor.age_range} | {actor.location}
                        </div>
                      </td>
                      <td>{actor.role_tags.join(", ")}</td>
                      <td>
                        {formatNumber(actor.fee_min)}-{formatNumber(actor.fee_max)}
                      </td>
                      <td>{actor.schedule_status}</td>
                      <td>
                        <div className="compact-actions">
                          <button className="button-secondary" onClick={() => startActorEdit(actor)} type="button">
                            <Edit3 size={14} />
                            编辑
                          </button>
                          <button className="button-danger" onClick={() => removeActor(actor.id)} type="button">
                            <Trash2 size={14} />
                            删除
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h2 className="panel-title">{editingActor ? "编辑演员" : "新建演员"}</h2>
              <p className="panel-subtitle">标签、题材、作品和风险项用英文逗号分隔。</p>
            </div>
            <form className="admin-form" onSubmit={handleActorSubmit}>
              <div className="field">
                <label>姓名</label>
                <input value={actorForm.name} onChange={(event) => setActorForm({ ...actorForm, name: event.target.value })} />
              </div>
              <div className="field">
                <label>性别</label>
                <select value={actorForm.gender} onChange={(event) => setActorForm({ ...actorForm, gender: event.target.value })}>
                  <option value="female">女</option>
                  <option value="male">男</option>
                </select>
              </div>
              <div className="field">
                <label>年龄段</label>
                <input value={actorForm.age_range} onChange={(event) => setActorForm({ ...actorForm, age_range: event.target.value })} />
              </div>
              <div className="field">
                <label>地区</label>
                <input value={actorForm.location} onChange={(event) => setActorForm({ ...actorForm, location: event.target.value })} />
              </div>
              <div className="field">
                <label>最低片酬</label>
                <input type="number" value={actorForm.fee_min} onChange={(event) => setActorForm({ ...actorForm, fee_min: Number(event.target.value) })} />
              </div>
              <div className="field">
                <label>最高片酬</label>
                <input type="number" value={actorForm.fee_max} onChange={(event) => setActorForm({ ...actorForm, fee_max: Number(event.target.value) })} />
              </div>
              <div className="field">
                <label>档期</label>
                <select value={actorForm.schedule_status} onChange={(event) => setActorForm({ ...actorForm, schedule_status: event.target.value })}>
                  <option value="available">available</option>
                  <option value="busy">busy</option>
                </select>
              </div>
              <div className="field">
                <label>粉丝数</label>
                <input type="number" value={actorForm.followers} onChange={(event) => setActorForm({ ...actorForm, followers: Number(event.target.value) })} />
              </div>
              <div className="field">
                <label>完播率</label>
                <input type="number" step="0.001" value={actorForm.completion_rate} onChange={(event) => setActorForm({ ...actorForm, completion_rate: Number(event.target.value) })} />
              </div>
              <div className="field">
                <label>付费转化</label>
                <input type="number" step="0.001" value={actorForm.paid_conversion_rate} onChange={(event) => setActorForm({ ...actorForm, paid_conversion_rate: Number(event.target.value) })} />
              </div>
              <div className="field">
                <label>形象标签</label>
                <input value={actorImageText} onChange={(event) => setActorImageText(event.target.value)} />
              </div>
              <div className="field">
                <label>角色标签</label>
                <input value={actorRoleText} onChange={(event) => setActorRoleText(event.target.value)} />
              </div>
              <div className="field">
                <label>题材</label>
                <input value={actorGenreText} onChange={(event) => setActorGenreText(event.target.value)} />
              </div>
              <div className="field">
                <label>代表作品</label>
                <input value={actorWorksText} onChange={(event) => setActorWorksText(event.target.value)} />
              </div>
              <div className="field">
                <label>风险项</label>
                <input value={actorRiskText} onChange={(event) => setActorRiskText(event.target.value)} />
              </div>
              {error ? <div className="error">{error}</div> : null}
              <button className="submit" type="submit">
                <Clapperboard size={16} />
                保存演员
              </button>
            </form>
          </section>
        </div> : null}

        {activeSection === "projects" ? <section className="panel">
          <div className="toolbar">
            <div>
              <h2 className="panel-title">项目库</h2>
              <p className="panel-subtitle">自动沉淀每次生成结果，支持回看评分、渠道、PDF 和核心内容。</p>
            </div>
            <button className="button-secondary" onClick={() => loadAdminData(token)} type="button">
              <RefreshCw size={14} />
              刷新
            </button>
          </div>
          <div className="project-library">
            <div className="section">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>项目</th>
                    <th>类型</th>
                    <th>渠道</th>
                    <th>评分</th>
                    <th>状态</th>
                    <th>查看</th>
                  </tr>
                </thead>
                <tbody>
                  {projects.map((project) => (
                    <tr className={selectedProject?.id === project.id ? "selected-row" : ""} key={project.id}>
                      <td>
                        <strong>{project.title}</strong>
                        <div className="creator-meta">{project.category}</div>
                        <div className="creator-meta">{formatIsoDate(project.updated_at)}</div>
                      </td>
                      <td>{projectKindLabel(project.kind)}</td>
                      <td>{project.platforms.join("、")}</td>
                      <td>{project.score ?? "-"}</td>
                      <td>{project.status}</td>
                      <td>
                        <button className="button-secondary" onClick={() => setSelectedProjectId(project.id)} type="button">
                          <Eye size={14} />
                          详情
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!projects.length ? <p className="admin-note">还没有项目。生成一次商单后会自动保存到这里。</p> : null}
            </div>
            <aside className="project-detail">
              {selectedProject ? (
                <>
                  <div className="project-detail-header">
                    <div>
                      <h3>{selectedProject.title}</h3>
                      <p>{projectKindLabel(selectedProject.kind)} | {formatIsoDate(selectedProject.created_at)}</p>
                    </div>
                    {selectedProject.pdf_url ? (
                      <a className="download" href={selectedProject.pdf_url} target="_blank" rel="noreferrer">
                        <Download size={14} />
                        PDF
                      </a>
                    ) : null}
                  </div>
                  <div className="project-detail-grid">
                    <div>
                      <span>预算</span>
                      <strong>{formatNumber(selectedProject.budget)}</strong>
                    </div>
                    <div>
                      <span>评分</span>
                      <strong>{selectedProject.score ?? "-"}</strong>
                    </div>
                    <div>
                      <span>状态</span>
                      <strong>{selectedProject.status}</strong>
                    </div>
                  </div>
                  {selectedDramaReport ? (
                    <div className="project-detail-body">
                      <h4>历史内容决策</h4>
                      <p>这是为追溯保留的历史 Content Pack 记录。新的决策请使用 DecisionOS 工作台。</p>
                      <h4>决策信号</h4>
                      <p>{selectedDramaReport.recommendations.slice(0, 3).join("；")}</p>
                      <h4>资源候选</h4>
                      <p>{selectedDramaReport.actors.slice(0, 4).map((actor) => `${actor.role}-${actor.name}`).join("；")}</p>
                    </div>
                  ) : null}
                  {selectedCampaignReport ? (
                    <div className="project-detail-body">
                      <h4>达人推荐</h4>
                      <p>{selectedCampaignReport.creators.slice(0, 4).map((creator) => `${creator.name} ${creator.match_score}`).join("；")}</p>
                      <h4>ROI</h4>
                      <p>预估曝光 {formatNumber(selectedCampaignReport.roi.estimated_reach)}，预估转化 {formatNumber(selectedCampaignReport.roi.estimated_conversions)}。</p>
                      <h4>风险</h4>
                      <p>{selectedCampaignReport.risk.level}：{selectedCampaignReport.risk.flags.join("；")}</p>
                    </div>
                  ) : null}
                </>
              ) : (
                <p className="admin-note">选择一个项目查看详情。</p>
              )}
            </aside>
          </div>
        </section> : null}

        {activeSection === "reports" ? <section className="panel">
          <div className="toolbar">
            <div>
              <h2 className="panel-title">报告列表</h2>
              <p className="panel-subtitle">查看已生成的 PDF 商单报告。</p>
            </div>
          </div>
          <div className="section">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>文件</th>
                  <th>大小</th>
                  <th>生成时间</th>
                  <th>下载</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td>{report.filename}</td>
                    <td>{Math.round(report.size_bytes / 1024)} KB</td>
                    <td>{formatDate(report.created_at)}</td>
                    <td>
                      <a className="download" href={report.url} target="_blank" rel="noreferrer">
                        <Download size={14} />
                        PDF
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!reports.length ? <p className="admin-note">还没有生成报告。</p> : null}
          </div>
        </section> : null}

        {activeSection === "logs" ? <section className="panel">
          <div className="toolbar">
            <div>
              <h2 className="panel-title">日志管理</h2>
              <p className="panel-subtitle">查看后台登录、达人管理、报告生成等活动记录。</p>
            </div>
            <div className="compact-actions">
              <button className="button-secondary" onClick={() => loadLogs()} type="button">
                <RefreshCw size={14} />
                刷新
              </button>
              <button className="button-danger" onClick={clearActivityLogs} type="button">
                <Trash2 size={14} />
                清空
              </button>
            </div>
          </div>
          <div className="log-filters">
            <div className="field">
              <label>级别</label>
              <select value={logLevel} onChange={(event) => setLogLevel(event.target.value)}>
                <option value="">全部</option>
                <option value="info">info</option>
                <option value="warning">warning</option>
                <option value="error">error</option>
              </select>
            </div>
            <div className="field">
              <label>事件关键词</label>
              <input
                value={logEvent}
                onChange={(event) => setLogEvent(event.target.value)}
                placeholder="campaign / login / creator"
              />
            </div>
            <button className="button-secondary" onClick={() => loadLogs()} type="button">
              <Activity size={14} />
              筛选
            </button>
          </div>
          <div className="section">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>级别</th>
                  <th>事件</th>
                  <th>操作者</th>
                  <th>内容</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td>{new Date(log.created_at).toLocaleString("zh-CN")}</td>
                    <td>
                      <span className={`log-level log-level-${log.level}`}>{log.level}</span>
                    </td>
                    <td>{log.event}</td>
                    <td>{log.actor}</td>
                    <td>
                      {log.message}
                      {Object.keys(log.metadata).length ? (
                        <pre className="log-metadata">{JSON.stringify(log.metadata, null, 2)}</pre>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!logs.length ? <p className="admin-note">暂无日志。</p> : null}
          </div>
        </section> : null}
        </div>
      </div>
    </main>
  );
}
