from __future__ import annotations

from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from backend.core.schemas import DramaReport


def _x(text: object) -> str:
    return escape(str(text), quote=True)


def _doc_p(text: object, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{style_xml}<w:r><w:t>{_x(text)}</w:t></w:r></w:p>"


def _doc_bullets(items: list[str]) -> str:
    return "".join(_doc_p(f"- {item}") for item in items)


def build_drama_docx_outline(report: DramaReport, path: Path) -> Path:
    body: list[str] = [
        _doc_p(f"{report.title} 短剧剧本大纲", "Title"),
        _doc_p(f"题材：{report.genre}"),
        _doc_p(f"平台：{report.platform}"),
        _doc_p(f"预算：{report.budget:,.0f}"),
        _doc_p("一句话卖点", "Heading1"),
        _doc_p(report.story.logline),
        _doc_p("核心冲突", "Heading1"),
        _doc_p(report.story.core_conflict),
        _doc_p("人物小传", "Heading1"),
    ]
    for character in report.story.characters:
        body.append(_doc_p(f"{character.role} / {character.name}", "Heading2"))
        body.append(_doc_p(f"{character.archetype}。欲望：{character.desire}。冲突：{character.conflict}"))

    body.append(_doc_p("前 10 集大纲", "Heading1"))
    for outline in report.story.episode_outline[:10]:
        paid = "付费卡点" if outline.paid_point else "普通推进"
        body.append(_doc_p(f"第{outline.episode}集《{outline.title}》[{paid}]", "Heading2"))
        body.append(_doc_p(f"钩子：{outline.hook}"))
        body.append(_doc_p(f"剧情：{outline.plot}"))
        body.append(_doc_p(f"结尾：{outline.cliffhanger}"))

    body.append(_doc_p("分集付费点", "Heading1"))
    for item in report.commercial_pack.paid_point_plan:
        body.append(_doc_p(f"第{item.episode}集：{item.trigger}", "Heading2"))
        body.append(_doc_p(f"卡点文案：{item.paywall_copy}"))
        body.append(_doc_p(f"下一集承诺：{item.next_episode_promise}"))

    body.append(_doc_p("前三集脚本", "Heading1"))
    for script in report.story.first_3_scripts:
        body.append(_doc_p(f"第{script.episode}集《{script.title}》", "Heading2"))
        body.append(_doc_p("场景"))
        body.append(_doc_bullets(script.scenes))
        body.append(_doc_p("对白节拍"))
        body.append(_doc_bullets(script.dialogue_beats))
        body.append(_doc_p(f"结尾钩子：{script.cliffhanger}"))

    body.append(_doc_p("修改建议", "Heading1"))
    for item in report.script_doctor.revision_items:
        body.append(_doc_p(f"{item.target}：{item.suggestion} 示例：{item.example}"))

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {''.join(body)}
    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
  </w:body>
</w:document>"""
    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>
</w:styles>"""
    with ZipFile(path, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>""")
        docx.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/styles.xml", styles_xml)
    return path


def _slide_xml(title: str, lines: list[str]) -> str:
    paragraphs = "".join(
        f"<a:p><a:r><a:rPr lang=\"zh-CN\" sz=\"2200\"/><a:t>{_x(line)}</a:t></a:r></a:p>"
        for line in lines[:8]
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>
    <p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="685800" y="457200"/><a:ext cx="7772400" cy="800000"/></a:xfrm></p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="zh-CN" sz="3600" b="1"/><a:t>{_x(title)}</a:t></a:r></a:p></p:txBody>
    </p:sp>
    <p:sp><p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="685800" y="1500000"/><a:ext cx="7772400" cy="4400000"/></a:xfrm></p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/>{paragraphs}</p:txBody>
    </p:sp>
  </p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def build_drama_ppt_pitch(report: DramaReport, path: Path) -> Path:
    slides = [
        (report.title, [f"题材：{report.genre}", f"平台：{report.platform}", f"预算：{report.budget:,.0f}", report.story.logline]),
        ("项目判断", [f"爆款潜力：{report.story.score.blockbuster_potential}", f"预估 ROI：{report.roi.estimated_roi:.1%}", f"回本周期：{report.roi.payback_days}", report.creative_package.positioning]),
        ("爆款对标", [f"{item.title}：{item.selling_point}" for item in report.commercial_pack.benchmarks[:4]]),
        ("投流计划", report.creative_package.title_templates[:5] + report.creative_package.ab_test_angles[:3]),
        ("付费点设计", [f"第{item.episode}集：{item.paywall_copy}" for item in report.commercial_pack.paid_point_plan]),
        ("演员与制作", [f"{actor.role}：{actor.name}，匹配 {actor.match_score}" for actor in report.actors[:6]]),
        ("执行建议", report.recommendations[:6]),
    ]
    slide_count = len(slides)
    slide_id_list = "".join(f'<p:sldId id="{256 + index}" r:id="rId{index + 1}"/>' for index in range(slide_count))
    relationships = "".join(
        f'<Relationship Id="rId{index + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{index + 1}.xml"/>'
        for index in range(slide_count)
    )
    overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{index + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for index in range(slide_count)
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as pptx:
        pptx.writestr("[Content_Types].xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  {overrides}
</Types>""")
        pptx.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>""")
        pptx.writestr("ppt/presentation.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldIdLst>{slide_id_list}</p:sldIdLst>
  <p:sldSz cx="9144000" cy="5143500" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>""")
        pptx.writestr("ppt/_rels/presentation.xml.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{relationships}</Relationships>""")
        for index, (title, lines) in enumerate(slides, start=1):
            pptx.writestr(f"ppt/slides/slide{index}.xml", _slide_xml(title, lines))
            pptx.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>""")
    return path
