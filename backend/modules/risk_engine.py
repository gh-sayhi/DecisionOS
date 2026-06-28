from __future__ import annotations

from backend.core.schemas import CampaignRequest, MatchedCreator, RiskAssessment


SENSITIVE_TERMS = {
    "医美": "医疗/功效表达需合规审查",
    "减肥": "健康功效表达需避免绝对化",
    "收益": "收益承诺需加入风险提示",
    "最": "极限词需替换为可验证表述",
    "第一": "排名表述需提供证明材料",
}


def assess_risk(campaign: CampaignRequest, creators: list[MatchedCreator]) -> RiskAssessment:
    flags: list[str] = []
    text = f"{campaign.brand} {campaign.goal} {campaign.category or ''}"
    for term, message in SENSITIVE_TERMS.items():
        if term in text:
            flags.append(message)
    for creator in creators:
        for risk in creator.risk_flags:
            flags.append(f"{creator.name}: {risk}")

    unique_flags = sorted(set(flags))
    score = min(100, 20 + len(unique_flags) * 13 + (8 if campaign.budget > 200000 else 0))
    level = "low"
    if score >= 65:
        level = "high"
    elif score >= 40:
        level = "medium"

    mitigations = [
        "上线前进行脚本文案合规审核",
        "避免绝对化、功效承诺和未经证明的数据表述",
        "达人合同加入发布时间、素材授权、舆情处理和撤稿条款",
    ]
    if level == "high":
        mitigations.insert(0, "建议增加法务或品牌审核节点后再投放")

    return RiskAssessment(
        level=level,
        score=round(score, 2),
        flags=unique_flags or ["未发现明显高风险信号"],
        mitigations=mitigations,
    )
