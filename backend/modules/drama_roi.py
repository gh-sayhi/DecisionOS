from __future__ import annotations

from backend.core.schemas import DramaProjectRequest, DramaRoiForecast, MatchedActor


PLATFORM_MULTIPLIER = {
    "hongguo": 1.25,
    "红果": 1.25,
    "douyin": 1.1,
    "抖音": 1.1,
    "kuaishou": 1.0,
    "快手": 1.0,
    "reelshort": 1.35,
}


def forecast_drama_roi(project: DramaProjectRequest, actors: list[MatchedActor]) -> DramaRoiForecast:
    platform_multipliers = [PLATFORM_MULTIPLIER.get(platform.lower(), 1.0) for platform in project.platforms]
    platform_multiplier = sum(platform_multipliers) / max(len(platform_multipliers), 1)
    channel_lift = 1 + max(0, len(project.platforms) - 1) * 0.18
    avg_completion = sum(actor.completion_rate for actor in actors) / max(len(actors), 1)
    avg_paid = sum(actor.paid_conversion_rate for actor in actors) / max(len(actors), 1)
    actor_signal = sum(actor.followers for actor in actors) * 0.12
    base_views = project.budget * 18 * platform_multiplier * channel_lift + actor_signal
    genre_bonus = 1.12 if any(keyword in project.genre for keyword in ["甜宠", "逆袭", "霸总", "复仇"]) else 1.0
    estimated_views = int(base_views * genre_bonus)
    paid_conversion = max(0.012, avg_paid)
    arppu = 18 if project.monetization.upper() == "IAP" else 8
    revenue = estimated_views * paid_conversion * arppu
    profit = revenue - project.budget
    roi = profit / project.budget
    payback_days = "7-14天" if roi > 0.6 else "14-30天" if roi > 0 else "30天以上"

    return DramaRoiForecast(
        estimated_views=estimated_views,
        completion_rate=round(avg_completion, 3),
        paid_conversion_rate=round(paid_conversion, 3),
        estimated_revenue=round(revenue, 2),
        estimated_profit=round(profit, 2),
        estimated_roi=round(roi, 3),
        payback_days=payback_days,
        assumptions=[
            "播放量按预算、多渠道平台系数和演员账号信号估算",
            "付费转化率按推荐演员历史表现均值估算",
            "IAP 默认单付费用户收入按 18 元估算，可接入真实平台数据替换",
        ],
    )
