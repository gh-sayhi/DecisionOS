from __future__ import annotations

from backend.core.schemas import CampaignRequest, MatchedCreator, RoiForecast


def forecast_roi(campaign: CampaignRequest, creators: list[MatchedCreator]) -> RoiForecast:
    reach = sum(item.estimated_reach for item in creators)
    conversions = sum(item.estimated_conversions for item in creators)
    average_order_value = max(99, min(999, campaign.budget * 0.018))
    revenue = conversions * average_order_value
    roi = (revenue - campaign.budget) / campaign.budget
    cpc = campaign.budget / conversions if conversions else campaign.budget

    return RoiForecast(
        estimated_reach=reach,
        estimated_conversions=conversions,
        estimated_revenue=round(revenue, 2),
        estimated_roi=round(roi, 3),
        cost_per_conversion=round(cpc, 2),
        assumptions=[
            "曝光按达人粉丝量、预算和平均 CPM 综合估算",
            "转化按达人历史 conversion_rate 估算",
            "客单价默认按预算规模推断，可接入品牌真实 GMV 数据替换",
        ],
    )
