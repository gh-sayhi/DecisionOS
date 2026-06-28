from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.core.campaign_generator import generate_campaign
from backend.core.schemas import CampaignRequest


def main() -> None:
    report = generate_campaign(
        CampaignRequest(
            brand="Acme AI Notes",
            budget=50000,
            goal="提升 AI 效率工具新品认知，并获取试用转化",
            platform="douyin",
            category="tech",
            audience="一二线城市效率工具用户",
        )
    )
    pdf_path = ROOT / "output" / "reports" / f"{report.report_id}.pdf"
    print(report.model_dump_json(indent=2))
    print(f"PDF exists: {pdf_path.exists()} -> {pdf_path}")


if __name__ == "__main__":
    main()
