from __future__ import annotations

from fastapi import APIRouter

from backend.core.drama_generator import generate_drama_report
from backend.core.schemas import DramaProjectRequest, DramaReport, GrowthReviewRecord, GrowthReviewReport, GrowthReviewRequest, ProjectWorkspaceResponse
from backend.modules.growth_review import review_growth
from backend.services.storage import append_log, build_project_workspace, list_growth_reviews, save_growth_review_record


router = APIRouter(prefix="/api/drama", tags=["short-drama"])


@router.post("/generate", response_model=DramaReport)
def generate(project: DramaProjectRequest) -> DramaReport:
    report = generate_drama_report(project)
    append_log(
        "drama.report.generated",
        f"生成短剧选角报告 {report.report_id}",
        actor="user",
        metadata={
            "report_id": report.report_id,
            "title": report.title,
            "genre": report.genre,
            "budget": report.budget,
            "platforms": "、".join(report.platforms),
        },
    )
    return report


@router.post("/review", response_model=GrowthReviewReport)
def review(request: GrowthReviewRequest) -> GrowthReviewReport:
    report = review_growth(request)
    save_growth_review_record(request, report)
    append_log(
        "drama.growth.reviewed",
        f"复盘短剧投流数据 {request.project_title}",
        actor="user",
        metadata={
            "project_title": request.project_title,
            "platform": request.platform,
            "episode": request.episode,
            "winner": report.winner,
        },
    )
    return report


@router.get("/reviews", response_model=list[GrowthReviewRecord])
def reviews(project_title: str | None = None) -> list[GrowthReviewRecord]:
    return list_growth_reviews(project_title=project_title)


@router.get("/workspace", response_model=ProjectWorkspaceResponse)
def workspace() -> ProjectWorkspaceResponse:
    return build_project_workspace()
