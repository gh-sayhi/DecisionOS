from __future__ import annotations

from uuid import uuid4

from backend.core.schemas import CampaignReport, CampaignRequest
from backend.modules.creator_match import match_creators
from backend.modules.risk_engine import assess_risk
from backend.modules.roi_engine import forecast_roi
from backend.modules.script_gen import generate_scripts
from backend.services.pdf_report import build_pdf_report
from backend.services.storage import ensure_report_dir, load_creators


def generate_campaign(campaign: CampaignRequest) -> CampaignReport:
    report_id = f"rpt_{uuid4().hex[:10]}"
    creators = match_creators(campaign, load_creators(), limit=3)
    scripts = generate_scripts(campaign, creators)
    risk = assess_risk(campaign, creators)
    roi = forecast_roi(campaign, creators)

    pdf_path = ensure_report_dir() / f"{report_id}.pdf"
    report = CampaignReport(
        report_id=report_id,
        brand=campaign.brand,
        budget=campaign.budget,
        goal=campaign.goal,
        platform=campaign.platform,
        creators=creators,
        scripts=scripts,
        risk=risk,
        roi=roi,
        pdf_url=f"/reports/{pdf_path.name}",
    )
    build_pdf_report(report, pdf_path)
    return report
