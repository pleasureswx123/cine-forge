from __future__ import annotations

import html
import os
import zipfile
from pathlib import Path


OUT = Path("docs/AI内容工业化平台建设方案-老板汇报版.pptx")
EMU = 914400
SLIDE_W = 12192000
SLIDE_H = 6858000
FONT = "Microsoft YaHei"


def emu(v: float) -> int:
    return int(v * EMU)


def esc(s: str) -> str:
    return html.escape(str(s), quote=False)


def fill_xml(color: str | None, alpha: int | None = None) -> str:
    if not color:
        return "<a:noFill/>"
    color = color.replace("#", "")
    alpha_xml = f'<a:alpha val="{alpha}"/>' if alpha is not None else ""
    return f'<a:solidFill><a:srgbClr val="{color}">{alpha_xml}</a:srgbClr></a:solidFill>'


def line_xml(color: str | None = None, width: int = 12700, alpha: int | None = None) -> str:
    if not color:
        return '<a:ln><a:noFill/></a:ln>'
    return f'<a:ln w="{width}">{fill_xml(color, alpha)}</a:ln>'


def text_body(lines, size=22, color="FFFFFF", bold=False, align="l", bullet=False) -> str:
    if isinstance(lines, str):
        lines = [lines]
    paras = []
    for line in lines:
        text = esc(line)
        bu = '<a:buChar char="•"/>' if bullet else ""
        paras.append(
            f'<a:p><a:pPr algn="{align}">{bu}'
            f'<a:defRPr sz="{size*100}" b="{1 if bold else 0}">'
            f'{fill_xml(color)}<a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/>'
            f'</a:defRPr></a:pPr><a:r><a:rPr lang="zh-CN" sz="{size*100}" b="{1 if bold else 0}">'
            f'{fill_xml(color)}<a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/></a:rPr>'
            f'<a:t>{text}</a:t></a:r><a:endParaRPr lang="zh-CN" sz="{size*100}"/></a:p>'
        )
    return '<p:txBody><a:bodyPr wrap="square" lIns="91440" tIns="45720" rIns="91440" bIns="45720"><a:spAutoFit/></a:bodyPr><a:lstStyle/>' + "".join(paras) + '</p:txBody>'


class Slide:
    def __init__(self, title: str, index: int, section: str = ""):
        self.title = title
        self.index = index
        self.section = section
        self.parts: list[str] = []
        self.sid = 2
        self.bg()

    def next_id(self) -> int:
        self.sid += 1
        return self.sid

    def bg(self):
        self.rect(0, 0, 13.333, 7.5, "0B1020", None, name="background")
        self.rect(0, 0, 13.333, 0.12, "4B7BFF", None, name="top-accent")
        self.rect(10.7, -0.25, 3.0, 1.3, "6C3BFF", None, alpha=45000, name="glow-1")
        self.rect(-0.7, 6.4, 3.5, 1.0, "00D4FF", None, alpha=25000, name="glow-2")

    def rect(self, x, y, w, h, fill="1E2A44", line="34537A", alpha=None, prst="roundRect", name="rect"):
        i = self.next_id()
        self.parts.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>{fill_xml(fill, alpha)}{line_xml(line)}</p:spPr></p:sp>'
        )

    def text(self, x, y, w, h, lines, size=22, color="FFFFFF", bold=False, align="l", bullet=False, fill=None, line=None, name="text"):
        i = self.next_id()
        self.parts.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill_xml(fill)}{line_xml(line)}</p:spPr>'
            f'{text_body(lines, size, color, bold, align, bullet)}</p:sp>'
        )

    def title_block(self, subtitle: str | None = None):
        self.text(0.55, 0.32, 8.9, 0.5, self.title, 26, "FFFFFF", True)
        if subtitle:
            self.text(0.6, 0.88, 10.8, 0.35, subtitle, 11, "A9B8D8")
        self.text(11.75, 0.38, 0.9, 0.3, f"{self.index:02d}", 13, "80E8FF", True, "r")

    def footer(self):
        self.text(0.55, 7.02, 4.5, 0.25, "AI 内容工业化平台建设方案", 8, "6F7F9E")
        self.text(12.1, 7.02, 0.55, 0.25, str(self.index), 8, "6F7F9E", align="r")

    def card(self, x, y, w, h, title, body="", icon="", color="223554"):
        self.rect(x, y, w, h, color, "456A9C")
        if icon:
            self.text(x + 0.12, y + 0.1, 0.55, 0.45, icon, 22, "80E8FF", True, "c")
            tx = x + 0.68
            tw = w - 0.82
        else:
            tx = x + 0.15
            tw = w - 0.3
        self.text(tx, y + 0.12, tw, 0.32, title, 13, "FFFFFF", True)
        if body:
            self.text(x + 0.18, y + 0.55, w - 0.36, h - 0.68, body, 9, "C7D2EE")

    def arrow(self, x, y, w, h, color="4B7BFF"):
        self.rect(x, y, w, h, color, None, prst="rightArrow", name="arrow")

    def table(self, x, y, col_ws, row_h, rows, header_color="273D63"):
        for r, row in enumerate(rows):
            xx = x
            fill = header_color if r == 0 else ("16233A" if r % 2 else "1D2D49")
            for c, cell in enumerate(row):
                self.rect(xx, y + r * row_h, col_ws[c], row_h, fill, "385C8C", prst="rect")
                self.text(xx + 0.04, y + r * row_h + 0.05, col_ws[c] - 0.08, row_h - 0.08, cell, 8 if len(str(cell)) > 16 else 9, "FFFFFF" if r == 0 else "DDE7FF", r == 0, "c")
                xx += col_ws[c]

    def finish(self) -> str:
        self.footer()
        sp_tree = '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>' + "".join(self.parts) + '</p:spTree>'
        return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld>{sp_tree}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'


def slide_cover():
    s = Slide("", 1)
    s.rect(0.8, 1.0, 11.7, 5.3, "111A2F", "315A96", alpha=None)
    s.text(1.15, 1.55, 10.9, 0.8, "AI 内容工业化平台建设方案", 34, "FFFFFF", True, "c")
    s.text(1.45, 2.45, 10.3, 0.45, "从小说文本到 AI Storyboard、镜头级视频生成与成片导出的生产闭环", 16, "80E8FF", True, "c")
    labels = [("小说文本", "📖"), ("剧本", "✍"), ("资产卡", "🧩"), ("Storyboard", "🎞"), ("视频生成", "▶"), ("成片导出", "🎬")]
    x = 1.2
    for i, (t, ico) in enumerate(labels):
        s.card(x, 3.45, 1.55, 0.82, t, "", ico, "1E3155")
        if i < len(labels) - 1:
            s.arrow(x + 1.58, 3.7, 0.38, 0.22)
        x += 1.95
    s.text(1.25, 5.15, 5.5, 0.35, "面向影视动漫 / 短剧 / 漫剧内容生产", 13, "C7D2EE")
    s.text(7.0, 5.15, 4.4, 0.35, "汇报人：XXX　日期：XXXX 年 XX 月 XX 日", 12, "C7D2EE", align="r")
    return s.finish()


def slide_cards(idx, title, subtitle, cards, cols=3):
    s = Slide(title, idx)
    s.title_block(subtitle)
    x0, y0 = 0.75, 1.45
    gap = 0.28
    w = (11.9 - gap * (cols - 1)) / cols
    h = 1.25 if len(cards) <= 6 else 1.0
    for i, c in enumerate(cards):
        row, col = divmod(i, cols)
        s.card(x0 + col * (w + gap), y0 + row * (h + 0.32), w, h, c[0], c[1], c[2] if len(c) > 2 else "", c[3] if len(c) > 3 else "223554")
    return s.finish()


def slide_table(idx, title, subtitle, rows, col_ws, x=0.85, y=1.55, row_h=0.55):
    s = Slide(title, idx)
    s.title_block(subtitle)
    s.table(x, y, col_ws, row_h, rows)
    return s.finish()


def slide_flow(idx, title, subtitle, nodes, y=2.35):
    s = Slide(title, idx)
    s.title_block(subtitle)
    x = 0.65
    w = 1.55 if len(nodes) >= 6 else 1.9
    for i, (name, icon, desc) in enumerate(nodes):
        s.card(x, y, w, 1.08, name, desc, icon, "1D3154")
        if i < len(nodes) - 1:
            s.arrow(x + w + 0.06, y + 0.42, 0.34, 0.22)
        x += w + 0.48
    return s.finish()


def build_slides() -> list[str]:
    slides = [slide_cover()]
    slides.append(slide_cards(2, "我们建议建设一套“AI 内容工业化平台”", "一句话结论：把影视动漫生产经验沉淀为结构化、可审核、可复用的 AI 生产流程", [
        ("输入", "小说文本 / 剧本 / 故事梗概", "📖", "1E3155"),
        ("中间层", "剧本、角色卡、场景卡、风格卡、Storyboard", "🧩", "243A65"),
        ("生成", "关键帧、参考图、视频片段、配音", "⚙", "294477"),
        ("沉淀", "项目资产库、提示词、参数、审核记录", "🗂", "1D4D63"),
    ], cols=4))
    slides.append(slide_cards(3, "AI 正在进入影视动漫内容生产的核心链路", "行业背景：从纯人工经验驱动，走向人工创意 + AI 辅助生产 + 平台化管理", [
        ("文本大模型", "小说理解、剧情拆解、剧本改写", "T", "1D3154"),
        ("图像生成", "角色图、场景图、风格图、关键帧", "I", "243A65"),
        ("视频生成", "镜头级视频片段、首帧/首尾帧控制", "V", "294477"),
        ("语音合成", "角色配音、旁白、声音测试", "A", "1D4D63"),
        ("自动剪辑", "字幕、拼接、预览、基础后期", "E", "20395B"),
        ("平台管理", "项目、资产、版本、成本、审核", "P", "263B5E"),
    ], cols=3))
    slides.append(slide_cards(4, "当前内容生产链路存在明显效率瓶颈", "传统流程长、协作岗位多、经验依赖强，缺少统一结构和资产沉淀机制", [
        ("前期拆解慢", "小说/故事到可制作内容周期长", "1"),
        ("沟通成本高", "编剧、美术、导演、后期反复对齐", "2"),
        ("设定反复改", "角色、场景、风格难稳定", "3"),
        ("流程割裂", "分镜、图像、视频生成缺少统一结构", "4"),
        ("资产难复用", "角色、道具、提示词散落在个人手里", "5"),
        ("经验难沉淀", "项目经验依赖个人，难以标准化", "6"),
    ], cols=3))
    slides.append(slide_table(5, "单句提示词生成视频，不适合工业化内容生产", "一句 Prompt 可以做 Demo，但难以支撑连续叙事、多镜头一致性和可修改流程", [
        ["问题", "具体表现", "平台化应对"],
        ["叙事不稳定", "镜头之间缺少连贯剧情", "先生成剧本与 Storyboard"],
        ["角色不一致", "人脸、服装、年龄、气质变化", "角色卡 + 参考图约束"],
        ["场景漂移", "同一空间在不同镜头中变化", "场景卡 + 不可变元素"],
        ["风格不统一", "色彩、光影、材质不连续", "风格卡 + 负向提示词"],
        ["修改困难", "不知道改提示词、图像还是视频", "镜头级任务 + 版本管理"],
    ], [2.1, 4.5, 4.5], row_h=0.68))
    slides.append(slide_flow(6, "平台核心思路：先结构化，再调用 AI 生成", "把剧情、人物、场景、风格和镜头先结构化，用中间层约束后续生成", [
        ("小说文本", "📖", "输入"), ("剧情分析", "AI", "结构化"), ("剧本改写", "✍", "可编辑"),
        ("资产卡", "🧩", "一致性"), ("Storyboard", "🎞", "镜头级"), ("视频生成", "▶", "候选片段"),
    ]))
    slides.append(slide_table(7, "项目定位：AI 内容工业化平台", "不是工具堆叠，而是围绕生产流程建设可管理、可审核、可复用的平台", [
        ["不是", "而是"],
        ["不是单一 AI 工具集合", "围绕影视动漫生产流程的平台"],
        ["不是一次性生成成片", "镜头级、版本化、可审核生产"],
        ["不是只保存结果文件", "沉淀角色、场景、提示词和参数"],
        ["不是完全自动化黑盒", "AI 生成 + 人工确认 + 版本保存"],
    ], [5.5, 5.5], y=1.6, row_h=0.78))
    slides.append(slide_flow(8, "从小说到成片的完整生产闭环", "输入小说文本，输出成片预览，并沉淀全过程资产", [
        ("小说", "📖", "输入"), ("分析", "AI", "梗概/人物/场景"), ("剧本", "✍", "分集/分场"),
        ("资产", "🧩", "角色/场景/风格"), ("分镜", "🎞", "镜头卡"), ("生成", "▶", "图像/视频/声音"),
    ], y=1.9))
    slides.append(slide_table(9, "关键节点必须保留人工确认和版本保存", "AI 生成初稿，人负责判断；系统负责保存正式版本并继续流转", [
        ["环节", "AI 负责", "人负责", "系统负责"],
        ["小说分析", "生成结构化分析", "判断准确性", "保存版本"],
        ["剧本改写", "生成剧本初稿", "修改剧情台词", "记录正式版本"],
        ["资产卡", "生成设定提示词", "调整形象风格", "绑定后续任务"],
        ["Storyboard", "拆分镜头", "确认镜头节奏", "创建镜头任务"],
        ["视频生成", "生成候选片段", "审核/重生成", "记录参数成本"],
    ], [2.0, 3.0, 3.0, 3.0], row_h=0.64))
    slides.append(slide_cards(10, "视频生成前，必须先建立六类核心中间层", "角色、场景、风格、道具、声音和 Storyboard 是控制一致性的关键", [
        ("AI 角色卡", "外形、服装、表情、动作、声音", "人"),
        ("AI 场景卡", "空间布局、光线、天气、不可变元素", "景"),
        ("AI 风格卡", "画风、色彩、光影、质感", "风"),
        ("AI 道具卡", "关键物件外观与叙事功能", "物"),
        ("AI 声音卡", "声线、语速、语气和环境声", "声"),
        ("AI Storyboard", "镜头编号、景别、机位、运镜、时长", "镜"),
    ], cols=3))
    slides.append(slide_cards(11, "平台自动组装镜头级生成任务", "用户不需要手写复杂单句提示词，系统按镜头整合资产约束和模型参数", [
        ("Storyboard", "镜头说明、景别、机位、运镜、时长", "🎞"),
        ("资产约束", "角色卡、场景卡、风格卡、道具卡、声音卡", "🧩"),
        ("提示词", "正向提示词 + 负向提示词 + 模板", "T"),
        ("参考素材", "角色图、场景图、首帧、尾帧、参考视频", "I"),
        ("模型参数", "模型、尺寸、时长、种子、参考强度", "⚙"),
        ("生成结果", "候选视频片段、多版本、审核状态", "▶"),
    ], cols=3))
    slides.append(slide_cards(12, "第一阶段建议建设 10 个核心模块", "围绕核心闭环选择最必要模块，避免大而全", [
        ("项目管理", "创建、状态、进度、版本", "1"), ("小说分析", "梗概、结构、人物、场景", "2"),
        ("剧本改写", "分集、分场、台词、旁白", "3"), ("角色卡", "外形、服装、表情、提示词", "4"),
        ("场景/风格卡", "空间、光影、色彩、质感", "5"), ("Storyboard", "镜头卡、景别、机位、运镜", "6"),
        ("镜头生成", "关键帧、视频片段、多版本", "7"), ("后期预览", "字幕、拼接、导出", "8"),
        ("模型适配", "文本、图像、视频、语音", "9"), ("资产库", "沉淀、检索、复用", "10"),
    ], cols=5))
    slides.append(slide_cards(13, "第一阶段先做最小可用闭环，不做大而全", "目标是验证从小说文本到视频片段和简单成片预览的可行性", [
        ("P0 必做", "项目创建、小说输入、AI 分析、剧本改写、人工审核", "✓", "1F4B60"),
        ("P0 必做", "角色/场景/风格卡、Storyboard、镜头提示词", "✓", "1F4B60"),
        ("P0 必做", "关键帧、视频片段、多版本审核、简单预览", "✓", "1F4B60"),
        ("暂不重点做", "复杂权限、完整多人协同、大规模资产市场", "—", "4A2F3A"),
        ("暂不重点做", "完整商业级后期、复杂 Agent 自主编排", "—", "4A2F3A"),
        ("验证重点", "流程、模型效果、成本、协作方式和资产沉淀", "★", "243A65"),
    ], cols=3))
    slides.append(slide_table(14, "建议按三阶段推进", "先验证闭环，再提升生产管理能力，最终形成平台化能力", [
        ["阶段", "建设重点", "目标"],
        ["阶段一：核心闭环验证", "小说 → 剧本 → 资产卡 → Storyboard → 视频片段 → 预览", "验证可行性"],
        ["阶段二：生产管理能力", "批量生成、多模型对比、审核流程、成本统计、失败案例库", "提升效率"],
        ["阶段三：平台化能力", "多项目、多团队、权限、API、私有化部署、工作流模板", "支撑规模化"],
    ], [2.7, 6.1, 2.2], y=1.8, row_h=0.9))
    slides.append(slide_cards(15, "第一阶段完成后，我们能看到什么成果", "形成可演示、可验证、可继续扩展的生产原型", [
        ("项目原型", "可操作工作台与核心流程", "P"), ("剧本中间稿", "AI 改写 + 人工编辑 + 版本", "S"),
        ("资产卡样例", "角色、场景、风格卡", "C"), ("Storyboard", "镜头卡、提示词、资产绑定", "B"),
        ("生成结果", "关键帧、参考图、视频片段", "V"), ("资产库结构", "提示词、参数、审核、失败案例", "A"),
    ], cols=3))
    slides.append(slide_table(16, "采用轻量、稳定、可扩展的技术架构", "工作流优先，复杂 Agent 框架后置；模型可替换，数据资产保留", [
        ["层级", "建议方案", "说明"],
        ["前端", "Next.js / React", "项目工作台、编辑、预览"],
        ["后端", "FastAPI / Node.js", "API、工作流、任务创建"],
        ["数据库", "PostgreSQL", "项目、版本、审核、状态"],
        ["对象存储", "MinIO / OSS / COS", "图片、视频、音频、导出文件"],
        ["任务队列", "Redis + Celery / BullMQ", "异步模型调用与视频处理"],
        ["模型适配", "Provider Adapter", "统一接入文本/图像/视频/语音"],
    ], [2.0, 3.8, 5.0], row_h=0.54))
    slides.append(slide_table(17, "项目推进的核心前提：可稳定调用大模型能力", "文本、图像、视频模型是第一阶段最核心的前置条件", [
        ["模型类型", "用途", "优先级"],
        ["文本大模型", "小说理解、剧情拆解、剧本改写、资产卡、Storyboard、提示词", "最高"],
        ["图像生成模型", "角色图、场景图、风格图、关键帧、首尾帧", "最高"],
        ["视频生成模型", "文生视频、图生视频、首帧/首尾帧视频", "最高"],
        ["语音生成模型", "配音、旁白、声音测试", "中"],
        ["字幕/识别模型", "字幕生成、音频转写", "中"],
    ], [2.4, 6.3, 2.3], row_h=0.64))
    slides.append(slide_table(18, "第一阶段需要小团队快速验证", "建议用小团队完成 8-12 周核心闭环原型", [
        ["角色", "人数", "职责"],
        ["产品负责人", "1", "流程设计、需求拆解、验收"],
        ["前端工程师", "1", "工作台、编辑器、资产管理、预览"],
        ["后端工程师", "1-2", "API、数据库、任务队列、版本管理"],
        ["AI/模型接入工程师", "1", "模型适配、提示词模板、结构化输出"],
        ["美术/编剧顾问", "各 1", "视觉审核、剧情分镜质量判断"],
        ["测试/项目协调", "1", "流程测试、样例验收、问题跟进"],
    ], [2.5, 1.3, 7.2], row_h=0.54))
    slides.append(slide_cards(19, "平台长期价值：效率提升 + 资产沉淀 + 生产标准化", "短期形成可演示原型，长期沉淀公司级 AI 内容生产基础设施", [
        ("提效", "缩短前期拆解和初稿生成时间", "↑"),
        ("降本", "降低重复沟通、重复设定和试错成本", "¥"),
        ("复用", "沉淀角色、场景、风格、提示词和参数", "R"),
        ("可控", "镜头级生成、人工审核、版本追溯", "C"),
        ("规模化", "支撑未来批量短剧、漫剧、动画分镜生产", "S"),
        ("方法论", "把项目经验沉淀为标准流程", "M"),
    ], cols=3))
    slides.append(slide_table(20, "风险可控，关键是分阶段和保留人工审核", "主要风险来自模型质量和范围失控，平台通过结构化流程降低风险", [
        ["风险", "应对策略"],
        ["平台目标过大", "分阶段建设，先完成核心闭环"],
        ["视频质量不稳定", "多版本生成 + 人工审核 + 重生成"],
        ["角色一致性不足", "角色卡 + 参考图 + 提示词模板"],
        ["场景漂移 / 风格不统一", "场景卡、风格卡、不可变元素、负向提示词"],
        ["成本不可控", "模型成本记录 + 任务级统计 + 预算预警"],
        ["模型变化快", "模型适配层，底层模型可替换"],
    ], [3.5, 7.5], row_h=0.55))
    slides.append(slide_cards(21, "本次需要管理层确认三件事", "建议启动第一阶段，用 1-2 个内容样例验证核心闭环", [
        ("是否立项", "批准第一阶段核心闭环原型建设", "1", "1F4B60"),
        ("资源投入", "确认预算、周期和团队投入", "2", "243A65"),
        ("试点方向", "确定内容样例与模型供应商接入方案", "3", "294477"),
    ], cols=3))
    s = Slide("AI 内容工业化平台：先建立流程，再放大产能", 22)
    s.title_block("结束语：这不是一次工具采购，而是面向未来内容生产方式的基础设施建设")
    s.text(1.1, 1.75, 11.2, 1.0, "从 AI 工具使用，走向 AI 内容工业化生产", 28, "FFFFFF", True, "c")
    s.text(1.4, 3.0, 10.5, 0.65, "建议从核心闭环开始，把公司内容生产经验沉淀为标准化流程和可复用资产。", 17, "80E8FF", True, "c")
    for i, txt in enumerate(["确认立项", "确认试点内容", "确认模型接入", "启动 8-12 周原型建设"]):
        s.card(1.1 + i * 3.0, 4.45, 2.45, 0.95, txt, "下一步行动", str(i + 1), "1F3B61")
    slides.append(s.finish())
    return slides


def content_types(n: int) -> str:
    overrides = ''.join([f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, n + 1)])
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>{overrides}</Types>'''


def presentation_xml(n: int) -> str:
    ids = ''.join([f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1, n + 1)])
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{n+1}"/></p:sldMasterIdLst><p:sldIdLst>{ids}</p:sldIdLst>
<p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle><a:defPPr><a:defRPr lang="zh-CN"/></a:defPPr></p:defaultTextStyle></p:presentation>'''


def presentation_rels(n: int) -> str:
    rels = ''.join([f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>' for i in range(1, n + 1)])
    rels += f'<Relationship Id="rId{n+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>'


ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>'''

SLIDE_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'''

MASTER_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>'''

LAYOUT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'''

SLIDE_MASTER = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>'''

SLIDE_LAYOUT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''

THEME = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="AI Cinema"><a:themeElements><a:clrScheme name="AI"><a:dk1><a:srgbClr val="0B1020"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1D2D49"/></a:dk2><a:lt2><a:srgbClr val="C7D2EE"/></a:lt2><a:accent1><a:srgbClr val="4B7BFF"/></a:accent1><a:accent2><a:srgbClr val="00D4FF"/></a:accent2><a:accent3><a:srgbClr val="6C3BFF"/></a:accent3><a:accent4><a:srgbClr val="28D17C"/></a:accent4><a:accent5><a:srgbClr val="FFB84D"/></a:accent5><a:accent6><a:srgbClr val="FF5C7A"/></a:accent6><a:hlink><a:srgbClr val="80E8FF"/></a:hlink><a:folHlink><a:srgbClr val="A78BFA"/></a:folHlink></a:clrScheme><a:fontScheme name="YaHei"><a:majorFont><a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/></a:majorFont><a:minorFont><a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/></a:minorFont></a:fontScheme><a:fmtScheme name="Default"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'''


def write_pptx(slides: list[str]):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides)))
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        z.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", MASTER_RELS)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", LAYOUT_RELS)
        z.writestr("ppt/theme/theme1.xml", THEME)
        for i, xml in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml", xml)
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", SLIDE_RELS)


if __name__ == "__main__":
    slides = build_slides()
    write_pptx(slides)
    print(f"created {OUT} ({OUT.stat().st_size} bytes, {len(slides)} slides)")