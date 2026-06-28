from __future__ import annotations

from backend.core.schemas import Actor, DramaProjectRequest, MatchedActor


ROLE_HINTS = {
    "女主": {"女主", "甜妹", "清冷", "御姐", "公主"},
    "男主": {"男主", "霸总", "总裁", "少年感", "叔系"},
    "反派": {"反派", "冷感", "权谋", "贵气"},
    "女二": {"女二", "闺蜜", "反派", "御姐"},
    "妈妈": {"妈妈", "家庭伦理", "贵气"},
}


def _terms(*values: str | None) -> set[str]:
    result: set[str] = set()
    for value in values:
        if not value:
            continue
        normalized = value.replace("，", ",").replace("/", ",").replace("、", ",")
        result.update(part.strip() for part in normalized.split(",") if part.strip())
        result.update(part.strip() for part in normalized.split() if part.strip())
    return result


def match_actors(project: DramaProjectRequest, actors: list[Actor], limit_per_role: int = 2) -> list[MatchedActor]:
    project_terms = _terms(project.genre, project.audience, project.synopsis)
    budget_per_role = project.budget * 0.42 / max(len(project.roles), 1)
    matched: list[MatchedActor] = []

    for role in project.roles:
        role_terms = ROLE_HINTS.get(role, {role}) | _terms(role)
        role_matches: list[MatchedActor] = []
        for actor in actors:
            actor_terms = set(actor.image_tags + actor.role_tags + actor.genres)
            role_hits = role_terms.intersection(actor_terms)
            genre_hits = project_terms.intersection(actor_terms)
            role_score = min(35, len(role_hits) * 14)
            genre_score = min(25, len(genre_hits) * 10)
            performance_score = min(20, actor.completion_rate * 35 + actor.paid_conversion_rate * 300)
            budget_score = 12 if actor.fee_min <= budget_per_role else max(0, 12 - (actor.fee_min - budget_per_role) / 8000)
            schedule_score = 8 if actor.schedule_status == "available" else 2
            score = role_score + genre_score + performance_score + budget_score + schedule_score

            budget_fit = "预算内" if actor.fee_min <= budget_per_role else "可能超预算"
            schedule_fit = "档期可用" if actor.schedule_status == "available" else "需确认档期"
            reasons = [
                f"角色标签命中: {', '.join(sorted(role_hits))}" if role_hits else "角色标签匹配较弱",
                f"题材标签命中: {', '.join(sorted(genre_hits))}" if genre_hits else "题材相关度一般",
                f"历史完播率 {actor.completion_rate:.1%}, 付费转化 {actor.paid_conversion_rate:.1%}",
                f"{budget_fit}, {schedule_fit}",
            ]
            role_matches.append(
                MatchedActor(
                    **actor.model_dump(),
                    role=role,
                    match_score=round(score, 2),
                    score_reasons=reasons,
                    budget_fit=budget_fit,
                    schedule_fit=schedule_fit,
                )
            )

        matched.extend(sorted(role_matches, key=lambda item: item.match_score, reverse=True)[:limit_per_role])
    return matched
