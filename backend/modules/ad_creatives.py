from __future__ import annotations

from backend.core.schemas import AdvertisingCreative, CreativePackage, DramaProjectRequest, StoryDevelopment


PLATFORM_TONE = {
    "hongguo": "强情绪、强反转、付费点前置",
    "douyin": "开场冲突更直接，标题要短促有画面",
    "kuaishou": "人物关系更接地气，台词更口语",
    "reelshort": "高概念关系冲突，英文市场可强化身份差和秘密",
    "tiktok": "前三秒必须给出视觉冲突或关系爆点",
}


def _genre_keywords(project: DramaProjectRequest) -> list[str]:
    text = f"{project.genre} {project.synopsis or ''}"
    result = []
    for keyword in ["甜宠", "逆袭", "复仇", "霸总", "家庭伦理", "职场", "古装", "真假千金", "契约婚姻"]:
        if keyword in text:
            result.append(keyword)
    return result or ["强冲突", "反转", "关系拉扯"]


def build_creative_package(project: DramaProjectRequest, story: StoryDevelopment) -> CreativePackage:
    keywords = _genre_keywords(project)
    lead = project.roles[0] if project.roles else "女主"
    second = project.roles[1] if len(project.roles) > 1 else "男主"
    platforms = project.platforms or ["hongguo"]
    tone_notes = [PLATFORM_TONE.get(platform.lower(), "按平台调整冲突尺度和台词密度") for platform in platforms]

    positioning = (
        f"{project.title}主打{'、'.join(keywords[:3])}，用{lead}低谷开场和{second}关键介入制造连续追更欲望。"
    )
    target_persona = project.audience or "18-35 岁女性用户，偏好高反转、高情绪密度和清晰爽点回收"
    paid_hook_strategy = "第3、6、10集设置强付费卡点，优先放身份反转、关系失控和关键证据。"

    title_templates = [
        f"她被全网嘲笑那天，{second}递来一份改变命运的合同",
        f"所有人都以为{lead}输了，直到真相在直播间曝光",
        f"被背叛后重回低谷，她这次不再求任何人",
        f"{second}说不救弱者，却为她打破了所有规则",
        f"第3集才知道，她的真实身份根本不简单",
        f"反派刚得意三秒，证据已经传到所有人手机里",
        f"她不是回来解释的，她是回来清算的",
        f"一场交易，把两个互不信任的人绑到了一起",
        f"预算不高也能拍：三场戏讲清压迫、交易和反击",
        f"这不是甜宠，是互相利用后的情感失控",
    ]

    cover_copy = [
        "全网羞辱后，她开始反击",
        "契约成立，复仇开局",
        "他不救弱者，只押赢家",
        "第3集身份反转",
        "证据公开，全场变脸",
        "她终于不再低头",
        "反派失控只差一步",
        "甜宠外壳，复仇内核",
    ]

    ab_test_angles = [
        "A版强调公开羞辱和爽点回收，测试完播率。",
        "B版强调男女主交易关系，测试点击率。",
        "C版强调身份秘密和付费卡点，测试付费转化。",
        "D版强调反派压迫，测试评论互动和追更意愿。",
    ]

    creatives: list[AdvertisingCreative] = []
    base_hooks = [
        f"{lead}被当众羞辱，所有人都等着看她崩溃。",
        f"{second}突然出现，说只给她一次翻身机会。",
        "反派以为证据已经被毁，却不知道全程正在直播。",
        "她签下合作协议那一刻，真正的复仇才开始。",
        "第3集身份线索曝光，前面的羞辱全部变成伏笔。",
        "她不是求原谅，而是逼所有人承认真相。",
        "他表面冷漠，实际每一步都在帮她设局。",
        "这场婚约不是爱情，是两个人共同的筹码。",
    ]
    for index, hook in enumerate(base_hooks, start=1):
        platform = platforms[(index - 1) % len(platforms)]
        creatives.append(
            AdvertisingCreative(
                platform=platform,
                angle=f"素材角度 {index}: {keywords[(index - 1) % len(keywords)]}",
                opening_hook=hook,
                script=[
                    "0-3秒：直接给冲突画面或羞辱现场，避免铺垫。",
                    f"3-8秒：抛出{lead}当前困境和反派压迫。",
                    f"8-15秒：让{second}介入，制造关系和利益反差。",
                    "15-25秒：展示第一次反击或证据线索。",
                    "结尾：停在身份、关系或证据悬念上，引导追更。",
                ],
                cta="继续看下一集，真相马上反转。",
            )
        )

    return CreativePackage(
        positioning=positioning,
        target_persona=target_persona,
        paid_hook_strategy=paid_hook_strategy,
        title_templates=title_templates,
        cover_copy=cover_copy,
        ab_test_angles=ab_test_angles,
        platform_notes=tone_notes,
        creatives=creatives,
    )
