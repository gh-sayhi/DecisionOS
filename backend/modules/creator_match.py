from __future__ import annotations

from backend.core.schemas import CampaignRequest, Creator, MatchedCreator


PLATFORM_ALIASES = {
    "douyin": {"douyin", "抖音", "short-video", "video"},
    "xiaohongshu": {"xiaohongshu", "小红书", "red", "lifestyle"},
    "bilibili": {"bilibili", "b站", "video", "tech"},
}


def _normalize_terms(*values: str | None) -> set[str]:
    terms: set[str] = set()
    for value in values:
        if not value:
            continue
        clean = value.lower().replace("，", ",").replace("/", ",")
        terms.update(part.strip() for part in clean.split(",") if part.strip())
        terms.update(word.strip() for word in clean.split() if word.strip())
    return terms


def match_creators(
    campaign: CampaignRequest,
    creators: list[Creator],
    limit: int = 3,
) -> list[MatchedCreator]:
    desired_terms = _normalize_terms(campaign.goal, campaign.category, campaign.audience)
    platform_terms = PLATFORM_ALIASES.get(campaign.platform.lower(), {campaign.platform.lower()})
    budget_per_creator = campaign.budget / max(limit, 1)

    matched: list[MatchedCreator] = []
    for creator in creators:
        tag_hits = desired_terms.intersection(set(creator.tags))
        platform_score = 25 if creator.platform.lower() in platform_terms else 8
        relevance_score = min(35, len(tag_hits) * 12)
        performance_score = min(25, creator.conversion_rate * 500)
        scale_score = min(15, creator.followers / 100000)
        cost_penalty = max(0, (creator.avg_cpm - budget_per_creator / 1000) * 0.04)
        score = max(0, platform_score + relevance_score + performance_score + scale_score - cost_penalty)

        estimated_reach = int(min(creator.followers * 0.22, budget_per_creator / max(creator.avg_cpm, 1) * 1000))
        estimated_conversions = int(estimated_reach * creator.conversion_rate)
        reasons = [
            f"平台与 {campaign.platform} 匹配" if platform_score >= 25 else "平台非首选但可补充覆盖",
            f"标签命中: {', '.join(sorted(tag_hits))}" if tag_hits else "基于历史转化率补充推荐",
            f"历史转化率 {creator.conversion_rate:.1%}",
        ]

        matched.append(
            MatchedCreator(
                **creator.model_dump(),
                match_score=round(score, 2),
                score_reasons=reasons,
                estimated_reach=estimated_reach,
                estimated_conversions=estimated_conversions,
            )
        )

    return sorted(matched, key=lambda item: item.match_score, reverse=True)[:limit]
