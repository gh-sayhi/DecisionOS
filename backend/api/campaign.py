from __future__ import annotations

from fastapi import APIRouter

from backend.core.campaign_generator import generate_campaign
from backend.core.drama_generator import generate_drama_report
from backend.core.schemas import CampaignReport, CampaignRequest, DramaProjectRequest, DramaReport
from backend.services.storage import append_log, save_project_record


router = APIRouter(prefix="/api/campaign", tags=["campaign"])


@router.post("/generate", response_model=CampaignReport)
def generate(campaign: CampaignRequest) -> CampaignReport:
    report = generate_campaign(campaign)
    # 每次生成报告都沉淀成项目，后台项目库可以直接回看历史结果。
    save_project_record(
        report_id=report.report_id,
        kind="brand",
        title=report.brand,
        category=report.goal,
        platforms=[report.platform],
        budget=report.budget,
        score=int(report.roi.estimated_roi * 100),
        pdf_url=report.pdf_url,
        report=report.model_dump(),
    )
    append_log(
        "campaign.report.generated",
        f"生成商单报告 {report.report_id}",
        actor="user",
        metadata={
            "report_id": report.report_id,
            "brand": report.brand,
            "budget": report.budget,
            "platform": report.platform,
        },
    )
    return report


@router.post("/drama/generate", response_model=DramaReport)
def generate_drama_campaign(project: DramaProjectRequest) -> DramaReport:
    report = generate_drama_report(project)
    # 短剧项目额外保存剧本评分，方便后台按项目质量快速筛选。
    save_project_record(
        report_id=report.report_id,
        kind="drama",
        title=report.title,
        category=report.genre,
        platforms=report.platforms,
        budget=report.budget,
        score=report.story.score.overall,
        pdf_url=report.pdf_url,
        report=report.model_dump(),
    )
    append_log(
        "campaign.drama.generated",
        f"生成短剧商单报告 {report.report_id}",
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
