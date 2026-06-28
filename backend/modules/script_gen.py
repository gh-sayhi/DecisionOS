from __future__ import annotations

from backend.core.schemas import CampaignRequest, MatchedCreator, ScriptIdea


def generate_scripts(campaign: CampaignRequest, creators: list[MatchedCreator]) -> list[ScriptIdea]:
    scripts: list[ScriptIdea] = []
    for creator in creators:
        strongest_tag = creator.tags[0] if creator.tags else "lifestyle"
        scripts.append(
            ScriptIdea(
                creator_id=creator.id,
                hook=f"如果你正在为{campaign.goal}纠结，{campaign.brand}可能是一个更省力的答案。",
                structure=[
                    f"3秒痛点: 用{strongest_tag}场景切入目标人群的真实问题",
                    f"15秒体验: 展示{campaign.brand}如何降低决策或使用成本",
                    "10秒证据: 用对比、数据或用户反馈证明卖点",
                    "5秒转化: 给出限时权益、试用入口或评论关键词",
                ],
                cta=f"评论区输入品牌关键词，领取{campaign.brand}专属方案。",
            )
        )
    return scripts
