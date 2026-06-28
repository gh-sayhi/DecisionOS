from __future__ import annotations

from uuid import uuid4

from backend.core.schemas import DramaProjectRequest, DramaReport
from backend.modules.actor_match import match_actors
from backend.modules.ad_creatives import build_creative_package
from backend.modules.commercial_pack import build_commercial_decision_pack
from backend.modules.drama_risk import assess_drama_risk
from backend.modules.drama_roi import forecast_drama_roi
from backend.modules.script_doctor import build_script_doctor_report
from backend.modules.story_development import develop_story
from backend.services.office_export import build_drama_docx_outline, build_drama_ppt_pitch
from backend.services.pdf_report import build_drama_pdf_report
from backend.services.storage import ensure_report_dir, load_actors


def generate_drama_report(project: DramaProjectRequest) -> DramaReport:
    report_id = f"drama_{uuid4().hex[:10]}"
    actors = match_actors(project, load_actors(), limit_per_role=2)
    roi = forecast_drama_roi(project, actors)
    risk = assess_drama_risk(project, actors)
    story = develop_story(project, actors)
    creative_package = build_creative_package(project, story)
    script_doctor = build_script_doctor_report(project, story)
    commercial_pack = build_commercial_decision_pack(project, story)
    recommendations = [
        "先用前三集脚本和 6-8 条投流素材做小预算测试，再决定是否扩拍。",
        "优先锁定每个核心角色的第一推荐演员，同时保留第二推荐作为档期替补。",
        "第3、6、10集重点强化人设反差、情绪冲突和付费卡点。",
        "用爆款对标拆解确认开场钩子、付费卡点和低成本场景是否成立。",
        "把 PDF 立项书、PPT 提案包和 Word 剧本大纲拆成三类交付，分别服务老板、客户和执行团队。",
        "若预算紧张，优先保证男女主片酬、前三集拍摄质量和投流素材密度。",
        "开机前完成平台审核预检、合同授权确认、定妆素材测试和素材 A/B 测试计划。",
    ]

    pdf_path = ensure_report_dir() / f"{report_id}.pdf"
    ppt_path = ensure_report_dir() / f"{report_id}_pitch.pptx"
    docx_path = ensure_report_dir() / f"{report_id}_outline.docx"
    report = DramaReport(
        report_id=report_id,
        title=project.title,
        genre=project.genre,
        platform="、".join(project.platforms),
        platforms=project.platforms,
        budget=project.budget,
        roles=project.roles,
        actors=actors,
        roi=roi,
        risk=risk,
        story=story,
        creative_package=creative_package,
        script_doctor=script_doctor,
        commercial_pack=commercial_pack,
        recommendations=recommendations,
        pdf_url=f"/reports/{pdf_path.name}",
        ppt_url=f"/reports/{ppt_path.name}",
        docx_url=f"/reports/{docx_path.name}",
    )
    build_drama_pdf_report(report, pdf_path)
    build_drama_ppt_pitch(report, ppt_path)
    build_drama_docx_outline(report, docx_path)
    return report
