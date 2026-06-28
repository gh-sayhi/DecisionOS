from __future__ import annotations

from backend.core.schemas import (
    BenchmarkDrama,
    CommercialDecisionPack,
    DeliveryAsset,
    DramaProjectRequest,
    PaidPointPlan,
    StoryDevelopment,
)


def _has(project: DramaProjectRequest, keyword: str) -> bool:
    return keyword.lower() in f"{project.genre} {project.synopsis or ''}".lower()


def _benchmark_titles(project: DramaProjectRequest) -> list[BenchmarkDrama]:
    if _has(project, "出海") or _has(project, "reelshort"):
        return [
            BenchmarkDrama(
                title="契约婚姻出海型短剧",
                genre_fit="身份反转 + 高概念关系",
                selling_point="阶层差异、秘密身份和强情绪台词适合海外信息流快速理解。",
                opening_hook="女主在婚礼或宴会被当众羞辱，男主用一个条件把她拉回牌桌。",
                paid_hook="第3集揭开男主真实身份，第6集揭开婚约代价。",
                production_note="场景集中在豪宅、办公室、宴会厅，减少群演，强化服化道质感。",
            ),
            BenchmarkDrama(
                title="复仇女主逆袭型短剧",
                genre_fit="复仇 + 爽点回收",
                selling_point="主角从弱到强，天然适合用连续打脸剪成多条广告素材。",
                opening_hook="女主被夺走资源后发现关键证据，决定当场反击。",
                paid_hook="每次反击前先给用户看一半证据，把答案留到下一集。",
                production_note="优先拍摄反击现场、证据展示和围观反应，方便二创剪辑。",
            ),
        ]
    if _has(project, "古装"):
        return [
            BenchmarkDrama(
                title="错嫁王妃权谋型短剧",
                genre_fit="古装 + 身份错位",
                selling_point="身份误认、权谋试探和情感保护可以同时驱动付费。",
                opening_hook="女主替嫁入局，第一晚就发现自己只是棋子。",
                paid_hook="第3集暴露替嫁线索，第6集男主开始反向保护。",
                production_note="控制宫廷大场面，用宅院、书房、暗巷完成主要冲突。",
            ),
            BenchmarkDrama(
                title="重生复仇权臣型短剧",
                genre_fit="重生 + 复仇 + 权谋",
                selling_point="用户期待主角提前知道结局，并看她逐步改写命运。",
                opening_hook="主角带着上一世记忆醒来，第一件事就是避开死亡选择。",
                paid_hook="关键仇人每 3 集露出一次破绽，付费集给证据反杀。",
                production_note="服装和道具要服务身份层级，剧情重点放在语言交锋。",
            ),
        ]
    return [
        BenchmarkDrama(
            title="重生逆袭顶流型短剧",
            genre_fit="甜宠 + 逆袭 + 职场",
            selling_point="低谷羞辱、资源交易和公开反击是高转化短剧的稳定三件套。",
            opening_hook="女主在镜头前被旧关系背叛，下一秒拿到翻盘筹码。",
            paid_hook="第3集第一次打脸，第6集关系失控，第10集身份线索公开。",
            production_note="重点拍发布会、试镜、办公室三类高冲突低成本场景。",
        ),
        BenchmarkDrama(
            title="契约恋爱霸总型短剧",
            genre_fit="甜宠 + 霸总 + 契约",
            selling_point="强保护和误会解除适合女性用户连续追更。",
            opening_hook="女主被逼签下不公平协议，男主却在公开场合替她撑腰。",
            paid_hook="每次保护都附带更大的误会，把告白和真相延后到付费集。",
            production_note="用服装、车、办公室建立阶层差异，不依赖大场面。",
        ),
        BenchmarkDrama(
            title="家庭秘密反转型短剧",
            genre_fit="家庭伦理 + 秘密 + 逆袭",
            selling_point="亲情压迫和身份秘密容易制造评论区争议与转发。",
            opening_hook="主角被家人当众牺牲利益，却发现自己不是他们以为的身份。",
            paid_hook="第3集露出亲子或财产线索，第6集让压迫者付出第一次代价。",
            production_note="家庭、公司、医院走廊等可复用场景足够支撑前 10 集。",
        ),
    ]


def build_commercial_decision_pack(project: DramaProjectRequest, story: StoryDevelopment) -> CommercialDecisionPack:
    benchmarks = _benchmark_titles(project)
    paid_points = [
        PaidPointPlan(
            episode=3,
            trigger="第一次公开反击只赢一半",
            user_emotion="爽感刚出现，但真相还没完全揭开。",
            paywall_copy="她到底拿到了什么证据？下一集立刻反杀。",
            next_episode_promise="揭开幕后操盘者的第一个破绽。",
        ),
        PaidPointPlan(
            episode=6,
            trigger="关系线从合作变成失控保护",
            user_emotion="用户开始站 CP，同时担心两人互相误解。",
            paywall_copy="他为什么突然站在她这边？真相只差一步。",
            next_episode_promise="男主暴露关键资源，反派升级围堵。",
        ),
        PaidPointPlan(
            episode=10,
            trigger="身份或核心秘密被关键人物看见",
            user_emotion="用户想确认主角是否彻底翻盘。",
            paywall_copy="所有人都以为她输了，只有她知道底牌已经亮出。",
            next_episode_promise="进入第二阶段大反击，旧关系开始崩塌。",
        ),
    ]
    delivery_assets = [
        DeliveryAsset(
            name="PDF 立项书",
            format="PDF",
            audience="老板、投资人、制片负责人",
            content=["项目定位", "爆款对标", "ROI 与风险", "演员建议", "投流素材摘要"],
        ),
        DeliveryAsset(
            name="PPT 提案包",
            format="PPT",
            audience="内部评审会、客户提案、招商沟通",
            content=["一句话卖点", "用户人群", "商业测算", "对标拆解", "拍摄计划"],
        ),
        DeliveryAsset(
            name="Word 剧本大纲",
            format="DOCX",
            audience="编剧、导演、执行制片",
            content=["人物小传", "前 10 集大纲", "付费卡点", "前三集脚本", "修改建议"],
        ),
    ]
    pitch_summary = [
        f"这个项目的核心卖点是：{story.logline}",
        f"对标方向应选择“{benchmarks[0].genre_fit}”，先验证前三集钩子和第3集付费卡点。",
        "建议先用 3-5 万小预算投流测试标题、封面和前三秒素材，再决定是否扩拍。",
    ]
    rollout_checklist = [
        "开拍前确认前三集脚本、核心演员、三类封面和 6 条信息流脚本。",
        "上线首日记录曝光、CTR、3 秒留存、完播率、付费率和单集流失点。",
        "若 CTR 低于预期，先换标题封面；若完播低，重剪前三秒；若付费低，前移付费卡点。",
        "第3、6、10集分别做单独素材，验证反击、关系、身份三种付费驱动力。",
    ]
    return CommercialDecisionPack(
        benchmark_summary="对标拆解用于回答“为什么这个题材值得做”，重点看开场钩子、付费卡点和低成本可拍性。",
        benchmarks=benchmarks,
        paid_point_plan=paid_points,
        delivery_assets=delivery_assets,
        pitch_summary=pitch_summary,
        rollout_checklist=rollout_checklist,
    )
