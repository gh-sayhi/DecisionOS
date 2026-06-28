from __future__ import annotations

from backend.core.schemas import DramaProjectRequest, DramaRiskAssessment, MatchedActor


SENSITIVE_GENRES = {
    "医疗": "医疗相关剧情需避免专业诊疗误导",
    "金融": "金融收益情节需避免投资承诺",
    "未成年": "未成年人相关剧情需强化审核",
    "擦边": "擦边表达存在平台审核风险",
}


def assess_drama_risk(project: DramaProjectRequest, actors: list[MatchedActor]) -> DramaRiskAssessment:
    flags: list[str] = []
    text = f"{project.genre} {project.synopsis or ''}"
    for keyword, message in SENSITIVE_GENRES.items():
        if keyword in text:
            flags.append(message)
    for actor in actors:
        if actor.schedule_status != "available":
            flags.append(f"{actor.name}: 档期需二次确认")
        for flag in actor.risk_flags:
            flags.append(f"{actor.name}: {flag}")
        if actor.budget_fit != "预算内":
            flags.append(f"{actor.name}: 片酬可能超出角色预算")

    unique_flags = sorted(set(flags))
    score = min(100, 18 + len(unique_flags) * 12 + (8 if project.shooting_days < 5 else 0))
    level = "low" if score < 40 else "medium" if score < 68 else "high"

    mitigations = [
        "开机前确认主演档期和违约条款",
        "前三集增加冲突密度和付费卡点复核",
        "对敏感题材、极端台词和擦边镜头做平台审核预检",
        "演员合同明确肖像权、二创授权、补拍义务和尾款节点",
    ]
    return DramaRiskAssessment(
        level=level,
        score=round(score, 2),
        flags=unique_flags or ["未发现明显高风险信号"],
        mitigations=mitigations,
    )
