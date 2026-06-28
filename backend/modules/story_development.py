from __future__ import annotations

from backend.core.schemas import (
    CharacterProfile,
    DramaProjectRequest,
    EpisodeOutline,
    EpisodeScript,
    MatchedActor,
    ScriptScore,
    StoryDevelopment,
)


GENRE_PROMISES = {
    "甜宠": "高密度关系拉扯、误会解除和双向奔赴",
    "逆袭": "低谷压迫、身份翻盘和连续打脸爽点",
    "复仇": "秘密揭露、反制布局和阶段性清算",
    "霸总": "强势保护、阶层差异和情感反差",
    "古装": "身份错位、权谋试探和宿命感",
    "家庭伦理": "亲情压迫、秘密爆雷和情绪宣泄",
}


# 根据题材关键词提炼用户预期，比如甜宠要关系拉扯，逆袭要连续打脸。
def _has(project: DramaProjectRequest, keyword: str) -> bool:
    text = f"{project.genre} {project.synopsis or ''}"
    return keyword in text


def _primary_actor(actors: list[MatchedActor], role: str) -> MatchedActor | None:
    candidates = [actor for actor in actors if actor.role == role]
    return max(candidates, key=lambda item: item.match_score, default=None)


def _role_archetype(role: str, project: DramaProjectRequest) -> str:
    if "女主" in role:
        return "被低估的高潜力主角" if _has(project, "逆袭") else "情绪入口型女主"
    if "男主" in role:
        return "冷面高压保护者" if _has(project, "霸总") or _has(project, "甜宠") else "关键资源型男主"
    if "反派" in role:
        return "持续压迫型反派"
    return "推动冲突的功能型角色"


def develop_story(project: DramaProjectRequest, actors: list[MatchedActor]) -> StoryDevelopment:
    # 优先用匹配到的演员姓名生成角色内容，让剧本方案和选角结果联动。
    lead_role = project.roles[0] if project.roles else "女主"
    second_role = project.roles[1] if len(project.roles) > 1 else "男主"
    lead_actor = _primary_actor(actors, lead_role)
    second_actor = _primary_actor(actors, second_role)
    lead_name = lead_actor.name if lead_actor else lead_role
    second_name = second_actor.name if second_actor else second_role

    promise_parts = [value for key, value in GENRE_PROMISES.items() if _has(project, key)]
    if not promise_parts:
        promise_parts = ["强冲突开场、快速反转和清晰付费钩子"]

    # 结构建议面向短剧制片决策，重点回答“前三集怎么抓人”和“哪里付费”。
    logline = (
        f"{project.title}讲述{lead_role}{lead_name}在{project.genre}结构中被迫跌入低谷，"
        f"借助{second_role}{second_name}的关键资源完成反击，并在情感与利益冲突中做出选择。"
    )
    core_conflict = "主角想证明自己并夺回主动权，但反派持续利用身份、资源和误会制造压迫。"
    relationship_hook = f"{lead_role}与{second_role}从互不信任到利益绑定，再到情感失控，关系推进承担主要付费欲望。"
    audience_promise = "；".join(promise_parts)
    structure_suggestions = [
        "前三集采用“公开羞辱-利益交易-第一次反击”的短链路，先让用户看见压迫和爽点回收。",
        "每集控制在一个核心冲突内，结尾必须留下身份、关系或证据类悬念，方便连续追更。",
        "第3、6、10集设置强付费卡点，优先放身份反转、关系失控或关键证据出现。",
        f"围绕{lead_role}和{second_role}做强关系钩子，减少支线人物，保证短周期拍摄效率。",
        "多渠道投放时保留同一主线，但按渠道微调开场尺度、台词密度和付费点前置程度。",
    ]

    characters: list[CharacterProfile] = []
    # 人物小传保持短而可拍，避免生成太文学化、难落地的设定。
    for role in project.roles:
        actor = _primary_actor(actors, role)
        actor_name = actor.name if actor else role
        characters.append(
            CharacterProfile(
                role=role,
                name=actor_name,
                archetype=_role_archetype(role, project),
                desire="获得尊严、资源和情感主动权" if "女主" in role else "守住利益秩序并控制关键关系",
                conflict="被旧关系、误会或利益集团持续压制",
            )
        )

    outline: list[EpisodeOutline] = []
    total_outline = min(max(project.episodes, 10), 60)
    # 先生成最多 60 集大纲；前 10 集用于前端和 PDF 展示。
    for episode in range(1, total_outline + 1):
        paid_point = episode in {3, 6, 10} or episode % 8 == 0
        if episode == 1:
            title = "低谷开场"
            hook = "主角在最公开的场合被羞辱，核心矛盾立即曝光。"
            plot = "主角失去资源和信任，被迫接受一个看似不可能的机会。"
            cliffhanger = f"{second_role}突然出现，提出一个改变局势的条件。"
        elif episode == 2:
            title = "交易成立"
            hook = "主角为了翻身接受高风险合作。"
            plot = "两位核心角色建立利益绑定，反派开始第一次试探。"
            cliffhanger = "主角发现旧失败背后另有操盘者。"
        elif episode == 3:
            title = "第一次反击"
            hook = "主角抓住漏洞完成小胜。"
            plot = "反派被短暂压制，但更大的秘密被牵出。"
            cliffhanger = "付费点：主角身份线索被关键人物看见。"
        else:
            title = f"第{episode}次推进"
            hook = "新证据、新误会或新关系压力推动剧情加速。"
            plot = "主角获得阶段性筹码，反派制造新的舆论或情感压力。"
            cliffhanger = "结尾抛出关系反转或身份秘密。" if paid_point else "结尾留下下一集行动目标。"
        outline.append(EpisodeOutline(episode=episode, title=title, hook=hook, plot=plot, cliffhanger=cliffhanger, paid_point=paid_point))

    first_10_scripts: list[EpisodeScript] = []
    # 前 3 集给更具体的场景和对白，其余集保留可拍摄节拍作为后续扩展基础。
    for item in outline[:10]:
        if item.episode == 1:
            scenes = [
                f"场景1：发布会或公司大厅，{lead_role}被当众否定，旧关系借舆论把她推到低谷。",
                f"场景2：{lead_role}独自整理证据，发现自己失败不是能力问题，而是有人提前做局。",
                f"场景3：{second_role}出现，递出合作条件，要求她用一次公开反击证明价值。",
            ]
            dialogue_beats = [
                f"{lead_role}：今天你们让我低头，明天我会让所有人看见真相。",
                f"{second_role}：我不救弱者，我只投资还没输干净的人。",
                "反派：你手里那点证据，连进门的资格都没有。",
            ]
        elif item.episode == 2:
            scenes = [
                f"场景1：{lead_role}接受合作，但必须交出一个关键把柄作为交换。",
                f"场景2：{second_role}安排她重回核心场合，反派第一次试探两人的真实关系。",
                "场景3：主角从一份旧文件里发现幕后操盘者的痕迹，反击目标被重新锁定。",
            ]
            dialogue_beats = [
                f"{lead_role}：我可以签，但我的底线不是你能定价的。",
                f"{second_role}：底线留着，筹码拿出来。",
                "反派：你以为换个靠山，就能把过去洗干净？",
            ]
        elif item.episode == 3:
            scenes = [
                f"场景1：{lead_role}在直播、会议或试镜现场主动设局，让反派先暴露漏洞。",
                "场景2：证据被公开，主角完成第一次小胜，围观者态度开始反转。",
                "场景3：更大的身份线索突然出现，主角意识到自己重生或翻身背后另有代价。",
            ]
            dialogue_beats = [
                f"{lead_role}：你刚才承认的每一个字，都已经被所有人听见了。",
                f"{second_role}：做得不错，但你真正的敌人还没露面。",
                "反派：你赢了这一局，可你敢知道当年是谁推你下去的吗？",
            ]
        else:
            scenes = [
                f"场景A：用强冲突承接钩子，{item.hook}",
                f"场景B：角色做出选择，推动本集主线。{item.plot}",
                "场景C：用一句关键台词或动作把矛盾推向下一集。",
            ]
            dialogue_beats = [
                f"{lead_role}：我不是来求你们相信我的，我是来拿回属于我的东西。",
                f"{second_role}：你可以输一次，但不能输在同一个局里。",
                "反派：你以为翻身了？这才只是开始。",
            ]
        first_10_scripts.append(
            EpisodeScript(
                episode=item.episode,
                title=item.title,
                scenes=scenes,
                dialogue_beats=dialogue_beats,
                cliffhanger=item.cliffhanger,
            )
        )

    # 评分用于项目库排序和初筛，不替代人工判断，只提供生产风险参考。
    hook_score = 86 if _has(project, "逆袭") or _has(project, "甜宠") else 78
    actor_fit = int(sum(actor.match_score for actor in actors[: min(len(actors), 4)]) / max(min(len(actors), 4), 1))
    platform_fit = min(95, 76 + len(project.platforms) * 4)
    production_cost = 82 if project.shooting_days >= 7 else 70
    compliance = 68 if any(word in (project.synopsis or "") for word in ["擦边", "医疗", "金融"]) else 88
    score_values = {
        "hook": hook_score,
        "character": 84,
        "conflict": 86,
        "payoff": 82,
        "reversal": 80,
        "platform_fit": platform_fit,
        "actor_fit": actor_fit,
        "production_cost": production_cost,
        "compliance_risk": compliance,
        "blockbuster_potential": 84 if hook_score >= 84 and actor_fit >= 80 else 76,
    }
    overall = int(sum(score_values.values()) / len(score_values))
    notes = [
        "前3集具备清晰压迫、交易和第一次反击，适合先做投流测试。",
        "建议将第3、6、10集设置为强付费卡点。",
        "多渠道投放时需要按平台调整开场节奏和台词尺度。",
    ]

    return StoryDevelopment(
        logline=logline,
        core_conflict=core_conflict,
        relationship_hook=relationship_hook,
        audience_promise=audience_promise,
        structure_suggestions=structure_suggestions,
        characters=characters,
        episode_outline=outline,
        first_3_scripts=first_10_scripts[:3],
        first_10_scripts=first_10_scripts,
        score=ScriptScore(overall=overall, notes=notes, **score_values),
    )
