from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.core.schemas import CampaignReport, DramaReport


FONT_NAME = "STHeiti-Light"
FONT_PATH = "/System/Library/Fonts/STHeiti Light.ttc"

try:
    pdfmetrics.getFont(FONT_NAME)
except KeyError:
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CNTitle",
        parent=styles["Title"],
        fontName=FONT_NAME,
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#111827"),
        spaceAfter=14,
    )
)
styles.add(
    ParagraphStyle(
        name="CNHeading",
        parent=styles["Heading2"],
        fontName=FONT_NAME,
        fontSize=14,
        leading=20,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=12,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="CNBody",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=10,
        leading=15,
        wordWrap="CJK",
    )
)


def _p(text: object, style: str = "CNBody") -> Paragraph:
    return Paragraph(str(text), styles[style])


def build_pdf_report(report: CampaignReport, path: Path) -> Path:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"{report.brand} Campaign Report",
    )
    story = [
        _p(f"{report.brand} AI 商单决策报告", "CNTitle"),
        _p(f"目标：{report.goal}"),
        _p(f"平台：{report.platform} | 预算：{report.budget:,.0f}"),
        Spacer(1, 6 * mm),
        _p("达人推荐", "CNHeading"),
    ]

    creator_rows = [[_p("达人"), _p("分数"), _p("预估曝光"), _p("预估转化"), _p("推荐理由")]]
    for creator in report.creators:
        creator_rows.append(
            [
                _p(creator.name),
                _p(creator.match_score),
                _p(f"{creator.estimated_reach:,}"),
                _p(f"{creator.estimated_conversions:,}"),
                _p("；".join(creator.score_reasons)),
            ]
        )
    table = Table(creator_rows, colWidths=[34 * mm, 18 * mm, 27 * mm, 27 * mm, 66 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story += [table, _p("脚本方向", "CNHeading")]

    for script in report.scripts:
        story.append(_p(f"Hook：{script.hook}"))
        for step in script.structure:
            story.append(_p(f"- {step}"))
        story.append(_p(f"CTA：{script.cta}"))
        story.append(Spacer(1, 2 * mm))

    story += [
        _p("风险评估", "CNHeading"),
        _p(f"风险等级：{report.risk.level} | 风险分：{report.risk.score}"),
        _p("风险信号：" + "；".join(report.risk.flags)),
        _p("缓释建议：" + "；".join(report.risk.mitigations)),
        _p("ROI 预测", "CNHeading"),
        _p(f"预估曝光：{report.roi.estimated_reach:,}"),
        _p(f"预估转化：{report.roi.estimated_conversions:,}"),
        _p(f"预估收入：{report.roi.estimated_revenue:,.2f}"),
        _p(f"预估 ROI：{report.roi.estimated_roi:.1%}"),
        _p(f"单转化成本：{report.roi.cost_per_conversion:,.2f}"),
        _p("假设：" + "；".join(report.roi.assumptions)),
    ]
    doc.build(story)
    return path


def build_drama_pdf_report(report: DramaReport, path: Path) -> Path:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"{report.title} Casting Report",
    )
    story = [
        _p(f"{report.title} 短剧选角决策报告", "CNTitle"),
        _p(f"题材：{report.genre} | 平台：{report.platform} | 预算：{report.budget:,.0f}"),
        _p(f"角色需求：{'、'.join(report.roles)}"),
        Spacer(1, 6 * mm),
        _p("演员推荐", "CNHeading"),
    ]

    rows = [[_p("角色"), _p("演员"), _p("分数"), _p("预算"), _p("档期"), _p("推荐理由")]]
    for actor in report.actors:
        rows.append(
            [
                _p(actor.role),
                _p(actor.name),
                _p(actor.match_score),
                _p(actor.budget_fit),
                _p(actor.schedule_fit),
                _p("；".join(actor.score_reasons)),
            ]
        )
    table = Table(rows, colWidths=[22 * mm, 25 * mm, 16 * mm, 24 * mm, 24 * mm, 61 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story += [
        table,
        _p("播放与收益预测", "CNHeading"),
        _p(f"预估播放：{report.roi.estimated_views:,}"),
        _p(f"预估完播率：{report.roi.completion_rate:.1%}"),
        _p(f"预估付费转化：{report.roi.paid_conversion_rate:.1%}"),
        _p(f"预估收入：{report.roi.estimated_revenue:,.2f}"),
        _p(f"预估利润：{report.roi.estimated_profit:,.2f}"),
        _p(f"预估 ROI：{report.roi.estimated_roi:.1%} | 回本周期：{report.roi.payback_days}"),
        _p("风险评估", "CNHeading"),
        _p(f"风险等级：{report.risk.level} | 风险分：{report.risk.score}"),
        _p("风险信号：" + "；".join(report.risk.flags)),
        _p("缓释建议：" + "；".join(report.risk.mitigations)),
        _p("故事开发包", "CNHeading"),
        _p(f"一句话卖点：{report.story.logline}"),
        _p(f"核心冲突：{report.story.core_conflict}"),
        _p(f"关系钩子：{report.story.relationship_hook}"),
        _p(f"用户承诺：{report.story.audience_promise}"),
        _p("剧本结构建议", "CNHeading"),
    ]
    for suggestion in report.story.structure_suggestions:
        story.append(_p(f"- {suggestion}"))
    story += [
        _p("人物小传", "CNHeading"),
    ]
    for character in report.story.characters:
        story.append(
            _p(
                f"{character.role} / {character.name}：{character.archetype}。欲望：{character.desire}。冲突：{character.conflict}"
            )
        )

    score = report.story.score
    score_rows = [
        [_p("指标"), _p("分数"), _p("指标"), _p("分数")],
        [_p("钩子"), _p(score.hook), _p("人设"), _p(score.character)],
        [_p("冲突"), _p(score.conflict), _p("爽点"), _p(score.payoff)],
        [_p("反转"), _p(score.reversal), _p("平台适配"), _p(score.platform_fit)],
        [_p("演员适配"), _p(score.actor_fit), _p("制作成本"), _p(score.production_cost)],
        [_p("审核安全"), _p(score.compliance_risk), _p("爆款潜力"), _p(score.blockbuster_potential)],
        [_p("综合分"), _p(score.overall), _p(""), _p("")],
    ]
    score_table = Table(score_rows, colWidths=[36 * mm, 22 * mm, 36 * mm, 22 * mm], repeatRows=1)
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story += [
        _p("剧本评分", "CNHeading"),
        score_table,
        _p("评分建议：" + "；".join(score.notes)),
        _p("前10集分集大纲", "CNHeading"),
    ]
    for outline in report.story.episode_outline[:10]:
        paid = "付费卡点" if outline.paid_point else "普通推进"
        story.append(_p(f"第{outline.episode}集《{outline.title}》[{paid}]：{outline.plot} 结尾：{outline.cliffhanger}"))

    creative = report.creative_package
    story += [
        _p("投流素材包", "CNHeading"),
        _p(f"项目定位：{creative.positioning}"),
        _p(f"目标用户：{creative.target_persona}"),
        _p(f"付费钩子策略：{creative.paid_hook_strategy}"),
        _p("标题模板：" + "；".join(creative.title_templates[:8])),
        _p("封面文案：" + "；".join(creative.cover_copy[:8])),
        _p("A/B 测试角度：" + "；".join(creative.ab_test_angles)),
        _p("平台注意事项：" + "；".join(creative.platform_notes)),
    ]
    for item in creative.creatives[:6]:
        story.append(_p(f"{item.platform} / {item.angle}：{item.opening_hook}"))
        story.append(_p("脚本：" + "；".join(item.script)))
        story.append(_p(f"CTA：{item.cta}"))

    doctor = report.script_doctor
    story += [
        _p("剧本结构与优化建议", "CNHeading"),
        _p("剧本结构", "CNHeading"),
    ]
    for beat in doctor.structure:
        story.append(_p(f"{beat.stage}（第{beat.episodes}集）：{beat.purpose} 必备：{'；'.join(beat.must_have)}"))
    story.append(_p("内容优化", "CNHeading"))
    for item in doctor.content_optimizations:
        story.append(_p(f"- {item}"))
    story.append(_p("修改建议", "CNHeading"))
    for item in doctor.revision_items:
        story.append(_p(f"{item.target}：问题：{item.problem} 建议：{item.suggestion} 示例：{item.example}"))
    story.append(_p("台词改写示例", "CNHeading"))
    for item in doctor.dialogue_rewrites:
        story.append(_p(f"- {item}"))

    commercial = report.commercial_pack
    story += [
        _p("爆款对标与商业交付", "CNHeading"),
        _p(commercial.benchmark_summary),
    ]
    for item in commercial.benchmarks:
        story.append(_p(f"对标：{item.title}｜{item.genre_fit}"))
        story.append(_p(f"卖点：{item.selling_point}"))
        story.append(_p(f"前三秒：{item.opening_hook}"))
        story.append(_p(f"付费钩子：{item.paid_hook}"))
        story.append(_p(f"制作提示：{item.production_note}"))
    story.append(_p("分集付费点设计", "CNHeading"))
    for item in commercial.paid_point_plan:
        story.append(
            _p(
                f"第{item.episode}集：{item.trigger}。情绪：{item.user_emotion} "
                f"卡点文案：{item.paywall_copy} 下一集承诺：{item.next_episode_promise}"
            )
        )
    story.append(_p("一键交付包", "CNHeading"))
    for asset in commercial.delivery_assets:
        story.append(_p(f"{asset.name}（{asset.format}）给{asset.audience}：{'；'.join(asset.content)}"))
    story.append(_p("提案摘要：" + "；".join(commercial.pitch_summary)))
    story.append(_p("上线检查：" + "；".join(commercial.rollout_checklist)))

    story.append(_p("前三集具体内容", "CNHeading"))
    for script in report.story.first_3_scripts:
        story.append(_p(f"第{script.episode}集《{script.title}》"))
        story.append(_p("场景：" + "；".join(script.scenes)))
        story.append(_p("对白节拍：" + "；".join(script.dialogue_beats)))
        story.append(_p("结尾钩子：" + script.cliffhanger))

    story += [
        _p("执行建议", "CNHeading"),
    ]
    for recommendation in report.recommendations:
        story.append(_p(f"- {recommendation}"))
    story.append(_p("预测假设：" + "；".join(report.roi.assumptions)))
    doc.build(story)
    return path
