# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "snow_depth_inversion_flowchart.png"


def load_font(size, bold=False):
    candidates = [
        Path(r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf" if bold else r"C:\Windows\Fonts\simsun.ttc"),
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
    ]
    for font_path in candidates:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size=size)
    return ImageFont.load_default()


FONT_TITLE = load_font(46, bold=True)
FONT_HEADER = load_font(40, bold=True)
FONT_SUB = load_font(31, bold=True)
FONT_BODY = load_font(30)
FONT_SMALL = load_font(26)


W, H = 1900, 3080
MARGIN_X = 155
BOX_W = W - 2 * MARGIN_X
BLACK = (18, 18, 18)
GRID = (115, 115, 115)
LIGHT = (250, 250, 250)
HEADER_FILL = (235, 239, 244)
STEP_FILL = (255, 255, 255)
INNER_FILL = (247, 249, 252)
HILITE_FILL = (242, 247, 244)


img = Image.new("RGB", (W, H), "white")
draw = ImageDraw.Draw(img)


def text_width(text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def wrap_line(text, font, max_width):
    lines = []
    current = ""
    for ch in text:
        trial = current + ch
        if text_width(trial, font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def draw_text_block(x, y, w, lines, font=FONT_BODY, fill=BLACK, line_gap=10, center=False):
    cy = y
    for line in lines:
        if isinstance(line, tuple):
            text, local_font = line
        else:
            text, local_font = line, font
        wrapped = []
        for part in str(text).split("\n"):
            wrapped.extend(wrap_line(part, local_font, w))
        for item in wrapped:
            tx = x + (w - text_width(item, local_font)) / 2 if center else x
            draw.text((tx, cy), item, font=local_font, fill=fill)
            cy += text_height(item, local_font) + line_gap
    return cy


def rounded_box(x, y, w, h, r=18, fill=STEP_FILL, outline=BLACK, width=3):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=r, fill=fill, outline=outline, width=width)


def arrow_down(x, y1, y2):
    draw.line((x, y1, x, y2 - 22), fill=BLACK, width=4)
    draw.polygon([(x - 16, y2 - 22), (x + 16, y2 - 22), (x, y2 + 8)], fill=BLACK)


def arrow_right(x1, y, x2):
    draw.line((x1, y, x2 - 18, y), fill=BLACK, width=3)
    draw.polygon([(x2 - 18, y - 12), (x2 - 18, y + 12), (x2 + 4, y)], fill=BLACK)


def arrow_left(x1, y, x2):
    draw.line((x1, y, x2 + 18, y), fill=BLACK, width=3)
    draw.polygon([(x2 + 18, y - 12), (x2 + 18, y + 12), (x2 - 4, y)], fill=BLACK)


def step_box(y, h, title, code_label, detail_boxes, output_text=None, highlight_last=False):
    x = MARGIN_X
    rounded_box(x, y, BOX_W, h, r=16, fill=STEP_FILL)
    header_h = 72
    draw.rounded_rectangle((x, y, x + BOX_W, y + header_h), radius=16, fill=HEADER_FILL, outline=BLACK, width=3)
    draw.line((x, y + header_h, x + BOX_W, y + header_h), fill=BLACK, width=3)
    header = f"{title}    {code_label}"
    draw.text((x + (BOX_W - text_width(header, FONT_HEADER)) / 2, y + 15), header, font=FONT_HEADER, fill=BLACK)

    content_x = x + 42
    content_y = y + header_h + 32
    content_w = BOX_W - 84

    cols = 3
    gap_x = 26
    gap_y = 22
    inner_w = (content_w - gap_x * (cols - 1)) / cols
    inner_h = 122
    for idx, block in enumerate(detail_boxes):
        row = idx // cols
        col = idx % cols
        bx = content_x + col * (inner_w + gap_x)
        by = content_y + row * (inner_h + gap_y)
        fill = HILITE_FILL if highlight_last and idx == len(detail_boxes) - 1 else INNER_FILL
        rounded_box(bx, by, inner_w, inner_h, r=12, fill=fill, outline=GRID, width=2)
        title_text, body_text = block
        draw_text_block(bx + 18, by + 15, inner_w - 36, [(title_text, FONT_SUB), (body_text, FONT_SMALL)], line_gap=6)
        if col < cols - 1 and idx + 1 < len(detail_boxes):
            arrow_right(bx + inner_w + 5, by + inner_h / 2, bx + inner_w + gap_x - 7)
        elif col == cols - 1 and idx + 1 < len(detail_boxes):
            next_bx = content_x
            next_by = content_y + (row + 1) * (inner_h + gap_y)
            draw.line((bx + inner_w / 2, by + inner_h + 5, bx + inner_w / 2, next_by - 18), fill=BLACK, width=3)
            draw.line((bx + inner_w / 2, next_by - 18, next_bx - 20, next_by - 18), fill=BLACK, width=3)
            draw.line((next_bx - 20, next_by - 18, next_bx - 20, next_by + inner_h / 2), fill=BLACK, width=3)
            arrow_right(next_bx - 20, next_by + inner_h / 2, next_bx - 5)

    if output_text:
        out_y = y + h - 72
        draw.line((x, out_y - 12, x + BOX_W, out_y - 12), fill=GRID, width=2)
        draw_text_block(x + 42, out_y, BOX_W - 84, [("输出：" + output_text, FONT_SUB)], line_gap=5)


def iteration_box(y, h):
    x = MARGIN_X
    rounded_box(x, y, BOX_W, h, r=16, fill=STEP_FILL)
    header_h = 72
    draw.rounded_rectangle((x, y, x + BOX_W, y + header_h), radius=16, fill=HEADER_FILL, outline=BLACK, width=3)
    draw.line((x, y + header_h, x + BOX_W, y + header_h), fill=BLACK, width=3)
    header = "步骤4：参数迭代反演    snow_reterival.m"
    draw.text((x + (BOX_W - text_width(header, FONT_HEADER)) / 2, y + 15), header, font=FONT_HEADER, fill=BLACK)

    content_x = x + 42
    content_y = y + header_h + 28
    content_w = BOX_W - 84
    cols = 3
    gap_x = 26
    gap_y = 20
    inner_w = (content_w - gap_x * (cols - 1)) / cols
    inner_h = 126
    blocks = [
        ("有效剖面", "0 ≤ Depth_o < 20 m\nSc 负值与空值清理"),
        ("初始化", "k_a=0.07\n阈值 0.001，最多 100 次"),
        ("光程分布", "L=2z\np_L=β(z)exp(k_aL)"),
        ("反照率", "a=∫β dL / ∫p_L dL\n并限制 a<0.99"),
        ("路径矩", "H=<L>/2\nk_sd=<L²>/H³"),
        ("参数更新", "R=(1/k_a)((1-a)/8.43)²\nk_d=0.65√(k_a/R)"),
    ]
    for idx, block in enumerate(blocks):
        row = idx // cols
        col = idx % cols
        bx = content_x + col * (inner_w + gap_x)
        by = content_y + row * (inner_h + gap_y)
        rounded_box(bx, by, inner_w, inner_h, r=12, fill=INNER_FILL, outline=GRID, width=2)
        draw_text_block(bx + 18, by + 14, inner_w - 36, [(block[0], FONT_SUB), (block[1], FONT_SMALL)], line_gap=5)
        if col < cols - 1:
            arrow_right(bx + inner_w + 5, by + inner_h / 2, bx + inner_w + gap_x - 7)
        elif row == 0:
            next_bx = content_x
            next_by = content_y + inner_h + gap_y
            draw.line((bx + inner_w / 2, by + inner_h + 5, bx + inner_w / 2, next_by - 16), fill=BLACK, width=3)
            draw.line((bx + inner_w / 2, next_by - 16, next_bx - 20, next_by - 16), fill=BLACK, width=3)
            draw.line((next_bx - 20, next_by - 16, next_bx - 20, next_by + inner_h / 2), fill=BLACK, width=3)
            arrow_right(next_bx - 20, next_by + inner_h / 2, next_bx - 5)

    loop_x = content_x + inner_w + gap_x
    loop_y = content_y + 2 * (inner_h + gap_y) + 10
    loop_w = inner_w
    loop_h = 116
    rounded_box(loop_x, loop_y, loop_w, loop_h, r=12, fill=HILITE_FILL, outline=GRID, width=2)
    draw_text_block(loop_x + 18, loop_y + 16, loop_w - 36, [
        ("收敛判定", FONT_SUB),
        ("k_a' = k_d²/[3(k_sd+k_a)]", FONT_SMALL),
        ("|k_a'-k_a| < 0.001", FONT_SMALL),
    ], line_gap=4)

    left_bx = content_x
    right_bx = content_x + 2 * (inner_w + gap_x)
    second_row_y = content_y + inner_h + gap_y
    draw.line((right_bx + inner_w / 2, second_row_y + inner_h + 5, right_bx + inner_w / 2, loop_y + loop_h / 2), fill=BLACK, width=3)
    arrow_left(right_bx + inner_w / 2, loop_y + loop_h / 2, loop_x + loop_w + 3)
    draw.text((loop_x + loop_w + 28, loop_y + loop_h / 2 - 40), "否", font=FONT_SMALL, fill=BLACK)
    draw.line((loop_x, loop_y + loop_h / 2, content_x - 28, loop_y + loop_h / 2), fill=BLACK, width=3)
    draw.line((content_x - 28, loop_y + loop_h / 2, content_x - 28, content_y + inner_h / 2), fill=BLACK, width=3)
    arrow_right(content_x - 28, content_y + inner_h / 2, content_x - 5)
    draw.text((content_x + 12, loop_y + loop_h / 2 - 42), "否，更新 k_a 后重复", font=FONT_SMALL, fill=BLACK)

    yes_x = content_x + 2 * (inner_w + gap_x)
    yes_y = loop_y
    yes_w = inner_w
    yes_h = loop_h
    rounded_box(yes_x, yes_y, yes_w, yes_h, r=12, fill=HILITE_FILL, outline=GRID, width=2)
    draw_text_block(yes_x + 18, yes_y + 18, yes_w - 36, [
        ("收敛输出", FONT_SUB),
        ("snow=H_final", FONT_SMALL),
        ("snowA=a_final", FONT_SMALL),
    ], line_gap=5)
    arrow_right(loop_x + loop_w + 8, loop_y + loop_h / 2, yes_x - 8)

    out_y = y + h - 72
    draw.line((x, out_y - 12, x + BOX_W, out_y - 12), fill=GRID, width=2)
    draw_text_block(x + 42, out_y, BOX_W - 84, [("输出：沿轨雪深 snow、反照率 snowA、剖面经纬度 data_So", FONT_SUB)], line_gap=5)


def final_box(y, text):
    x = MARGIN_X
    rounded_box(x, y, BOX_W, 118, r=16, fill=LIGHT)
    draw.text((x + (BOX_W - text_width(text, FONT_HEADER)) / 2, y + 30), text, font=FONT_HEADER, fill=BLACK)


top_y = 55
rounded_box(MARGIN_X, top_y, BOX_W, 120, r=16, fill=LIGHT)
top_text = "输入：ATL03 强束光子观测、研究区范围、场景条件与系统响应"
draw.text((MARGIN_X + (BOX_W - text_width(top_text, FONT_TITLE)) / 2, top_y + 28), top_text, font=FONT_TITLE, fill=BLACK)

y1 = 235
arrow_down(W / 2, top_y + 120, y1 - 20)
step_box(
    y1,
    330,
    "步骤1：数据读取与场景裁剪",
    "ATL03_Read",
    [
        ("读取强束", "提取 initial_h、initial_t、经纬度"),
        ("质量与背景", "保留有效光子\n插值 back_ground_save"),
        ("场景裁剪", "按研究区、白天/夜间\n和高程范围筛选"),
    ],
    "有效 ATL03 光子集合与背景噪声信息",
)

y2 = 625
arrow_down(W / 2, y1 + 330, y2 - 18)
step_box(
    y2,
    520,
    "步骤2：表面定位与剖面构建",
    "f_ocean_choose / f_profile_processing",
    [
        ("主表面识别", "在 rel_t-height 空间\n做二维直方图"),
        ("表面序列修正", "插值空 bin、剔除跳点\nrloess 平滑"),
        ("表面对齐", "h_aligned=initial_h-surface\n深度 z=-h_aligned"),
        ("二维分箱", "按 0.15 m 深度网格\n构建 bin_matrix"),
        ("滑动聚合", "dt_int=4 s\nstep_t=0.5 s"),
        ("背景扣除", "-15 至 -5 m 估计 noise\nS<=0 置为 NaN"),
    ],
    "Depth、S、data_S、noise，即表面对齐后的后向散射剖面",
)

y3 = 1205
arrow_down(W / 2, y2 + 520, y3 - 18)
step_box(
    y3,
    390,
    "步骤3：系统响应去卷积",
    "f_deconvolution.m",
    [
        ("截取剖面", "保留 Depth_o≥-3 m\n表面以下进入求解"),
        ("系统响应", "读取 SystemResponse_try1.mat\n使用 SR_maxNorm"),
        ("线性反演", "构造卷积矩阵 F\n逐剖面求解 F·Sc=So"),
    ],
    "So、Sc、Depth_o、data_So，其中 Sc 为校正后剖面",
)

y4 = 1655
arrow_down(W / 2, y3 + 390, y4 - 18)
iteration_box(y4, 680)

y5 = 2395
arrow_down(W / 2, y4 + 680, y5 - 18)
step_box(
    y5,
    375,
    "步骤5：结果组织与验证准备",
    "run_ocean_choose.m",
    [
        ("保存结果", "Result*.mat\nsnow、data_S、snowA"),
        ("无效值处理", "空剖面、未收敛剖面\n保持为 NaN"),
        ("沿轨汇总", "组合经纬度、雪深\n和反照率序列"),
    ],
    "可与 OIB、UA、CMC 等验证数据匹配的沿轨雪深结果",
)

y6 = 2830
arrow_down(W / 2, y5 + 375, y6 - 16)
final_box(y6, "最终输出：ICESat-2 沿轨雪深产品与第四章验证分析输入")

draw_text_block(
    MARGIN_X,
    H - 82,
    BOX_W,
    ["注：流程依据 ATL03_Read 与 Snow 模块代码整理，变量名与核心公式保留代码实现含义。"],
    font=FONT_SMALL,
    fill=(80, 80, 80),
    center=True,
)

img.save(OUTPUT, dpi=(450, 450))
