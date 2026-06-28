from __future__ import annotations

from backend.core.schemas import GrowthReviewReport, GrowthReviewRequest, MaterialTestInput, MaterialTestResult, RewriteAssistantPack, RewriteSuggestion


def _rate(part: float, total: float) -> float:
    if total <= 0:
        return 0
    return round(part / total, 4)


def _roi(revenue: float, spend: float) -> float:
    if spend <= 0:
        return 0
    return round((revenue - spend) / spend, 4)


def _diagnose(test: MaterialTestInput, ctr: float, three_second_rate: float, completion_rate: float, paid_rate: float, roi: float) -> tuple[str, list[str], list[str]]:
    diagnosis: list[str] = []
    actions: list[str] = []
    score = 0

    if ctr < 0.012:
        diagnosis.append("点击率偏低，优先怀疑标题、封面和人群定向。")
        actions.append("重做标题和封面，前三个字直接放冲突或身份反转。")
    else:
        score += 1

    if three_second_rate < 0.35:
        diagnosis.append("3 秒留存偏低，前三秒钩子没有快速交代压迫、反转或关系张力。")
        actions.append("重剪开场，把羞辱、证据、反击或强关系动作前置到第 1 秒。")
    else:
        score += 1

    if completion_rate < 0.18:
        diagnosis.append("完播率偏低，素材中段节奏或信息密度不足。")
        actions.append("删掉铺垫台词，每 5-7 秒增加一次新信息或情绪转折。")
    else:
        score += 1

    if paid_rate < 0.015:
        diagnosis.append("付费率偏低，卡点承诺不够明确或付费前爽点回收过早。")
        actions.append("把付费点移到证据将公开、关系将失控、身份将揭晓的前一秒。")
    else:
        score += 1

    if roi < 0:
        diagnosis.append("ROI 为负，当前素材不适合继续放量。")
        actions.append("先小预算重测，不要直接扩大消耗。")
    else:
        score += 1

    if score >= 4:
        status = "保留放量"
        actions.insert(0, "保留该版本，下一轮只微调标题和前 3 秒。")
    elif score >= 2:
        status = "重剪复测"
    else:
        status = "下线重做"

    if not diagnosis:
        diagnosis.append("核心指标健康，可以作为下一轮 A/B 测试基准版本。")
    return status, diagnosis, actions


def _first_non_empty(values: list[str], fallback: str) -> str:
    return next((value for value in values if value.strip()), fallback)


def _build_rewrite_assistant(request: GrowthReviewRequest, tests: list[MaterialTestInput], results: list[MaterialTestResult], winner: str | None) -> RewriteAssistantPack:
    winner_test = next((test for test in tests if test.name == winner), None) or (tests[0] if tests else None)
    weak_result = min(results, key=lambda item: (item.ctr, item.three_second_rate, item.paid_rate), default=None)
    title_seed = _first_non_empty([winner_test.title if winner_test else ""], f"{request.project_title}第{request.episode}集")
    cover_seed = _first_non_empty([winner_test.cover_copy if winner_test else ""], "所有人都等她输")
    opening_seed = _first_non_empty([winner_test.opening_hook if winner_test else ""], "主角在公开场合被压迫")
    problem = "点击率、前三秒或付费率仍有提升空间"
    if weak_result and weak_result.diagnosis:
        problem = weak_result.diagnosis[0]

    title_options = [
        f"她被全场羞辱后，第{request.episode}集终于拿出底牌",
        f"所有人都以为她输了，下一秒反转开始",
        f"{title_seed}：证据公开前一秒，全场安静了",
        f"被背叛后她不哭了，直接让对手付出代价",
        f"他递来的不是合约，是她翻盘的最后机会",
    ]
    cover_options = [
        f"{cover_seed}，她却笑了",
        "全员围攻，她只亮出一张证据",
        "上一秒被羞辱，下一秒全场闭嘴",
        "别眨眼，她要开始反杀了",
        "他们赌她会输，她赌真相会赢",
    ]
    opening_recuts = [
        f"第 0-1 秒直接给冲突：{opening_seed}，画面上压大字“她被当众背叛”。",
        "第 1-3 秒切证据特写，不解释背景，只让用户知道反击马上发生。",
        "第 3-6 秒给反派一句狠话，再立刻切主角冷静回应，形成情绪反差。",
        "删掉铺垫镜头，把主角被压迫、证据出现、男主进场三件事压缩到 8 秒内。",
    ]
    paid_point_rewrites = [
        f"第{request.episode}集卡点：证据刚要公开时切断，文案写“她手里的东西，能毁掉所有人”。",
        "关系卡点：男主刚准备站队，反派先说出旧秘密，下一集承诺解释他为什么保护她。",
        "身份卡点：主角看见关键文件只露出第一页，下一集承诺揭开真正操盘者。",
        "爽点卡点：先让用户看到反派慌了，但把完整打脸留到下一集。",
    ]
    suggestions = [
        RewriteSuggestion(category="标题", target_problem="点击率不足时优先改标题前半句", options=title_options[:3]),
        RewriteSuggestion(category="封面", target_problem="封面要同时给压迫和反击预期", options=cover_options[:3]),
        RewriteSuggestion(category="前三秒", target_problem="3 秒留存不足时减少背景解释", options=opening_recuts[:3]),
        RewriteSuggestion(category="付费点", target_problem="付费率不足时把答案放到下一集", options=paid_point_rewrites[:3]),
    ]
    return RewriteAssistantPack(
        summary=f"基于当前复盘，下一轮围绕“{problem}”改写，保留胜出版本作为对照组，只测试标题、封面、前三秒、付费卡点四类变量。",
        title_options=title_options,
        cover_options=cover_options,
        opening_recuts=opening_recuts,
        paid_point_rewrites=paid_point_rewrites,
        suggestions=suggestions,
    )


def review_growth(request: GrowthReviewRequest) -> GrowthReviewReport:
    results: list[MaterialTestResult] = []
    for test in request.tests:
        ctr = _rate(test.clicks, test.impressions)
        three_second_rate = _rate(test.three_second_views, test.clicks)
        completion_rate = _rate(test.completions, test.clicks)
        paid_rate = _rate(test.paid_users, test.clicks)
        roi = _roi(test.revenue, test.spend)
        status, diagnosis, actions = _diagnose(test, ctr, three_second_rate, completion_rate, paid_rate, roi)
        results.append(
            MaterialTestResult(
                name=test.name,
                ctr=ctr,
                three_second_rate=three_second_rate,
                completion_rate=completion_rate,
                paid_rate=paid_rate,
                roi=roi,
                status=status,
                diagnosis=diagnosis,
                next_actions=actions,
            )
        )

    winner = max(results, key=lambda item: (item.roi, item.paid_rate, item.completion_rate, item.ctr)).name if results else None
    overall = [
        "先看点击率判断标题封面，再看 3 秒留存判断开场，最后看付费率判断剧情卡点。",
        f"当前平台为 {request.platform}，第 {request.episode} 集素材应优先验证一个核心情绪，不要同时测试太多变量。",
    ]
    if winner:
        overall.append(f"当前胜出版本是 {winner}，下一轮应以它为基准只改一个变量。")

    next_round = [
        "保留胜出版本作为对照组。",
        "新增一个标题强化版、一个封面强化版、一个前三秒重剪版。",
        "每个版本先跑相同小预算，至少拿到 3000 次曝光后再判断。",
        "若点击率提升但付费率不升，说明素材吸引力够但剧情卡点仍需重写。",
    ]
    rewrite_assistant = _build_rewrite_assistant(request, request.tests, results, winner)
    return GrowthReviewReport(
        project_title=request.project_title,
        platform=request.platform,
        episode=request.episode,
        winner=winner,
        overall_diagnosis=overall,
        test_results=results,
        next_round_plan=next_round,
        rewrite_assistant=rewrite_assistant,
    )
