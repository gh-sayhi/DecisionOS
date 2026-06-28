from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from backend.core.schemas import (
    Actor,
    ActorInput,
    Creator,
    CreatorInput,
    GrowthReviewRecord,
    GrowthReviewReport,
    GrowthReviewRequest,
    LogEntry,
    ProjectRecord,
    ProjectVersionSummary,
    ProjectWorkspaceGroup,
    ProjectWorkspaceResponse,
    ReportFile,
)


ROOT = Path(__file__).resolve().parents[2]
# 本项目先用本地 JSON 文件做轻量数据存储，方便 MVP 阶段直接查看和迁移。
CREATOR_DATA = ROOT / "backend" / "data" / "creators.json"
ACTOR_DATA = ROOT / "backend" / "data" / "actors.json"
LOG_DATA = ROOT / "backend" / "data" / "activity_logs.jsonl"
PROJECT_DATA = ROOT / "backend" / "data" / "projects.json"
GROWTH_REVIEW_DATA = ROOT / "backend" / "data" / "growth_reviews.json"
REPORT_DIR = ROOT / "output" / "reports"


def load_creators() -> list[Creator]:
    with CREATOR_DATA.open("r", encoding="utf-8") as file:
        rows = json.load(file)
    return [Creator(**row) for row in rows]


def save_creators(creators: list[Creator]) -> None:
    CREATOR_DATA.write_text(
        json.dumps([creator.model_dump() for creator in creators], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_creator(payload: CreatorInput) -> Creator:
    creators = load_creators()
    creator = Creator(id=f"cr_{uuid4().hex[:8]}", **payload.model_dump())
    creators.append(creator)
    save_creators(creators)
    append_log("admin.creator.created", f"新增达人 {creator.name}", actor="admin", metadata={"creator_id": creator.id})
    return creator


def update_creator(creator_id: str, payload: CreatorInput) -> Creator | None:
    creators = load_creators()
    for index, creator in enumerate(creators):
        if creator.id == creator_id:
            updated = Creator(id=creator_id, **payload.model_dump())
            creators[index] = updated
            save_creators(creators)
            append_log("admin.creator.updated", f"更新达人 {updated.name}", actor="admin", metadata={"creator_id": creator_id})
            return updated
    return None


def delete_creator(creator_id: str) -> bool:
    creators = load_creators()
    kept = [creator for creator in creators if creator.id != creator_id]
    if len(kept) == len(creators):
        return False
    save_creators(kept)
    append_log("admin.creator.deleted", f"删除达人 {creator_id}", actor="admin", metadata={"creator_id": creator_id})
    return True


def load_actors() -> list[Actor]:
    with ACTOR_DATA.open("r", encoding="utf-8") as file:
        rows = json.load(file)
    return [Actor(**row) for row in rows]


def save_actors(actors: list[Actor]) -> None:
    ACTOR_DATA.write_text(
        json.dumps([actor.model_dump() for actor in actors], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_actor(payload: ActorInput) -> Actor:
    actors = load_actors()
    actor = Actor(id=f"ac_{uuid4().hex[:8]}", **payload.model_dump())
    actors.append(actor)
    save_actors(actors)
    append_log("admin.actor.created", f"新增演员 {actor.name}", actor="admin", metadata={"actor_id": actor.id})
    return actor


def update_actor(actor_id: str, payload: ActorInput) -> Actor | None:
    actors = load_actors()
    for index, actor_item in enumerate(actors):
        if actor_item.id == actor_id:
            updated = Actor(id=actor_id, **payload.model_dump())
            actors[index] = updated
            save_actors(actors)
            append_log("admin.actor.updated", f"更新演员 {updated.name}", actor="admin", metadata={"actor_id": actor_id})
            return updated
    return None


def delete_actor(actor_id: str) -> bool:
    actors = load_actors()
    kept = [actor_item for actor_item in actors if actor_item.id != actor_id]
    if len(kept) == len(actors):
        return False
    save_actors(kept)
    append_log("admin.actor.deleted", f"删除演员 {actor_id}", actor="admin", metadata={"actor_id": actor_id})
    return True


def ensure_report_dir() -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    return REPORT_DIR


def list_reports() -> list[ReportFile]:
    # PDF 报告不进入数据库，直接扫描 output/reports 目录生成后台列表。
    report_dir = ensure_report_dir()
    reports: list[ReportFile] = []
    for path in sorted(report_dir.glob("*.pdf"), key=lambda item: item.stat().st_mtime, reverse=True):
        stat = path.stat()
        reports.append(
            ReportFile(
                id=path.stem,
                filename=path.name,
                url=f"/reports/{path.name}",
                size_bytes=stat.st_size,
                created_at=str(path.stat().st_mtime),
            )
        )
    return reports


def load_projects() -> list[ProjectRecord]:
    if not PROJECT_DATA.exists():
        return []
    with PROJECT_DATA.open("r", encoding="utf-8") as file:
        rows = json.load(file)
    return [ProjectRecord(**row) for row in rows]


def save_projects(projects: list[ProjectRecord]) -> None:
    PROJECT_DATA.parent.mkdir(parents=True, exist_ok=True)
    PROJECT_DATA.write_text(
        json.dumps([project.model_dump() for project in projects], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_project_record(
    *,
    report_id: str,
    kind: str,
    title: str,
    category: str,
    platforms: list[str],
    budget: float,
    report: dict,
    score: int | None = None,
    pdf_url: str | None = None,
    status: str = "已生成",
) -> ProjectRecord:
    # 项目库保存完整报告快照，后续即使演员库或达人库变化，历史结果仍可回看。
    projects = load_projects()
    now = datetime.now(timezone.utc).isoformat()
    existing = next((project for project in projects if project.report_id == report_id), None)
    project = ProjectRecord(
        id=existing.id if existing else f"prj_{uuid4().hex[:10]}",
        report_id=report_id,
        kind=kind,
        title=title,
        category=category,
        platforms=platforms,
        budget=budget,
        status=status,
        score=score,
        pdf_url=pdf_url,
        created_at=existing.created_at if existing else now,
        updated_at=now,
        report=report,
    )
    if existing:
        projects = [project if item.report_id == report_id else item for item in projects]
    else:
        projects.append(project)
    save_projects(projects)
    append_log(
        "admin.project.saved",
        f"保存项目 {project.title}",
        actor="system",
        metadata={"project_id": project.id, "report_id": report_id, "kind": kind},
    )
    return project


def get_project(project_id: str) -> ProjectRecord | None:
    return next((project for project in load_projects() if project.id == project_id), None)


def list_projects() -> list[ProjectRecord]:
    return sorted(load_projects(), key=lambda project: project.updated_at, reverse=True)


def load_growth_reviews() -> list[GrowthReviewRecord]:
    if not GROWTH_REVIEW_DATA.exists():
        return []
    with GROWTH_REVIEW_DATA.open("r", encoding="utf-8") as file:
        rows = json.load(file)
    return [GrowthReviewRecord(**row) for row in rows]


def save_growth_reviews(records: list[GrowthReviewRecord]) -> None:
    GROWTH_REVIEW_DATA.parent.mkdir(parents=True, exist_ok=True)
    GROWTH_REVIEW_DATA.write_text(
        json.dumps([record.model_dump() for record in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_growth_review_record(request: GrowthReviewRequest, report: GrowthReviewReport) -> GrowthReviewRecord:
    records = load_growth_reviews()
    record = GrowthReviewRecord(
        id=f"gr_{uuid4().hex[:10]}",
        project_title=request.project_title,
        platform=request.platform,
        episode=request.episode,
        winner=report.winner,
        created_at=datetime.now(timezone.utc).isoformat(),
        request=request,
        report=report,
    )
    records.append(record)
    save_growth_reviews(records)
    return record


def list_growth_reviews(project_title: str | None = None) -> list[GrowthReviewRecord]:
    records = load_growth_reviews()
    if project_title:
        records = [record for record in records if record.project_title == project_title]
    return sorted(records, key=lambda record: record.created_at, reverse=True)


def build_project_workspace() -> ProjectWorkspaceResponse:
    drama_projects = [project for project in list_projects() if project.kind == "drama"]
    reviews = list_growth_reviews()
    titles = sorted({project.title for project in drama_projects} | {review.project_title for review in reviews})
    groups: list[ProjectWorkspaceGroup] = []
    for title in titles:
        project_versions = [project for project in drama_projects if project.title == title]
        project_versions = sorted(project_versions, key=lambda project: project.created_at)
        versions = [
            ProjectVersionSummary(
                project_id=project.id,
                report_id=project.report_id,
                version_name=f"V{index + 1}",
                title=project.title,
                category=project.category,
                platforms=project.platforms,
                budget=project.budget,
                score=project.score,
                pdf_url=project.pdf_url,
                ppt_url=project.report.get("ppt_url") if isinstance(project.report, dict) else None,
                docx_url=project.report.get("docx_url") if isinstance(project.report, dict) else None,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
            for index, project in enumerate(project_versions)
        ]
        group_reviews = [review for review in reviews if review.project_title == title]
        groups.append(ProjectWorkspaceGroup(title=title, versions=versions, reviews=group_reviews))
    return ProjectWorkspaceResponse(groups=sorted(groups, key=lambda group: (len(group.versions), len(group.reviews), group.title), reverse=True))


def append_log(
    event: str,
    message: str,
    *,
    actor: str = "system",
    level: str = "info",
    metadata: dict[str, str | int | float | bool | None] | None = None,
) -> LogEntry:
    # 日志采用 jsonl 追加写入，避免频繁读写整个数组文件。
    LOG_DATA.parent.mkdir(parents=True, exist_ok=True)
    entry = LogEntry(
        id=f"log_{uuid4().hex[:12]}",
        created_at=datetime.now(timezone.utc).isoformat(),
        level=level,
        event=event,
        actor=actor,
        message=message,
        metadata=metadata or {},
    )
    with LOG_DATA.open("a", encoding="utf-8") as file:
        file.write(entry.model_dump_json() + "\n")
    return entry


def list_logs(limit: int = 200, event: str | None = None, level: str | None = None) -> list[LogEntry]:
    if not LOG_DATA.exists():
        return []
    entries: list[LogEntry] = []
    with LOG_DATA.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                entry = LogEntry(**json.loads(line))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            if event and event not in entry.event:
                continue
            if level and level != entry.level:
                continue
            entries.append(entry)
    return list(reversed(entries))[:limit]


def count_logs() -> int:
    if not LOG_DATA.exists():
        return 0
    with LOG_DATA.open("r", encoding="utf-8") as file:
        return sum(1 for line in file if line.strip())


def clear_logs(actor: str = "admin") -> None:
    LOG_DATA.parent.mkdir(parents=True, exist_ok=True)
    LOG_DATA.write_text("", encoding="utf-8")
    append_log("admin.logs.cleared", "清空活动日志", actor=actor, level="warning")
