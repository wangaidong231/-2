import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
import numpy as np
import io

# ================= 拼豆色卡（MARD 常用色） =================
PALETTE = {
    "A1": (255, 255, 255), "A2": (250, 240, 230), "A3": (245, 235, 220),
    "A4": (235, 215, 195), "A5": (225, 200, 175), "A6": (215, 185, 155),
    "A7": (205, 175, 145), "A8": (195, 165, 135),
    "B1": (255, 255, 200), "B2": (255, 245, 150), "B3": (255, 235, 100),
    "B4": (255, 215, 50),  "B5": (255, 195, 30),  "B6": (255, 175, 20),
    "B7": (255, 155, 10),  "B8": (240, 135, 10),
    "C1": (255, 220, 220), "C2": (255, 200, 200), "C3": (255, 175, 175),
    "C4": (255, 150, 150), "C5": (255, 120, 120), "C6": (255, 80, 80),
    "C7": (230, 50, 50),   "C8": (200, 30, 30),
    "D1": (240, 220, 255), "D2": (230, 200, 255), "D3": (215, 175, 255),
    "D4": (195, 145, 245), "D5": (170, 115, 230), "D6": (145, 85, 210),
    "D7": (120, 60, 185),
    "E1": (220, 235, 255), "E2": (190, 220, 255), "E3": (160, 200, 255),
    "E4": (130, 175, 245), "E5": (100, 150, 230), "E6": (70, 120, 210),
    "E7": (40, 90, 185),   "E8": (20, 60, 155),
    "F1": (220, 255, 220), "F2": (190, 245, 190), "F3": (160, 235, 160),
    "F4": (130, 220, 130), "F5": (100, 200, 100), "F6": (70, 175, 70),
    "F7": (40, 145, 40),   "F8": (20, 115, 20),
    "G1": (200, 190, 180), "G2": (180, 170, 160), "G3": (160, 150, 140),
    "G4": (140, 130, 120), "G5": (120, 110, 100), "G6": (100, 90, 80),
    "G7": (80, 70, 60),    "G8": (60, 50, 40),
    "H1": (200, 200, 200), "H2": (180, 180, 180), "H3": (140, 140, 140),
    "H4": (100, 100, 100), "H5": (60, 60, 60),    "H6": (30, 30, 30),
    "H7": (0, 0, 0),       "H8": (20, 20, 30),
}

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*[int(c) for c in rgb])

def find_closest_color(rgb, palette):
    min_dist = float('inf')
    closest = None
    for code, color in palette.items():
        dist = sum((rgb[i] - color[i]) ** 2 for i in range(3))
        if dist < min_dist:
            min_dist = dist
            closest = code
    return closest

def image_to_perler(img, grid_size, palette, scale=30, bg_color=(240,240,240)):
    """将PIL图片转换为拼豆图，返回PIL图片和颜色统计"""
    orig_w, orig_h = img.size
    aspect = orig_w / orig_h

    if aspect >= 1:
        new_w = grid_size
        new_h = int(grid_size / aspect)
    else:
        new_h = grid_size
        new_w = int(grid_size * aspect)
    new_w = max(1, new_w)
    new_h = max(1, new_h)

    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        resample_filter = Image.LANCZOS
    img_resized = img.resize((new_w, new_h), resample_filter)

    canvas = Image.new('RGB', (grid_size, grid_size), (255, 255, 255))  # 强制白色背景
    offset_x = (grid_size - new_w) // 2
    offset_y = (grid_size - new_h) // 2
    canvas.paste(img_resized, (offset_x, offset_y))
    img_array = np.array(canvas)

    perler_grid = []
    color_counts = Counter()
    for i in range(grid_size):
        row = []
        for j in range(grid_size):
            pixel = img_array[i, j]
            code = find_closest_color(pixel, palette)
            row.append(code)
            color_counts[code] += 1
        perler_grid.append(row)

    # 生成高清预览图
    output_size = grid_size * scale
    stat_height = 80 + 30 * ((len(color_counts) // 10) + 1)
    output_img = Image.new('RGB', (output_size, output_size + stat_height), color=(255,255,255))
    draw = ImageDraw.Draw(output_img)

    try:
        font_stat = ImageFont.truetype("arial.ttf", 16)
    except:
        font_stat = ImageFont.load_default()
    font_size = max(6, int(scale * 0.35))
    try:
        font_grid = ImageFont.truetype("arial.ttf", font_size)
    except:
        font_grid = ImageFont.load_default()

    # 绘制拼豆网格
    for i in range(grid_size):
        for j in range(grid_size):
            code = perler_grid[i][j]
            color = palette.get(code, (200,200,200))
            x0 = j * scale
            y0 = i * scale
            x1 = x0 + scale
            y1 = y0 + scale
            draw.rectangle([x0, y0, x1, y1], fill=rgb_to_hex(color), outline='#cccccc')
            if scale >= 10:
                brightness = 0.299*color[0] + 0.587*color[1] + 0.114*color[2]
                text_color = (0,0,0) if brightness > 128 else (255,255,255)
                bbox = draw.textbbox((0,0), code, font=font_grid)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                tx = x0 + (scale - text_w) // 2
                ty = y0 + (scale - text_h) // 2
                draw.text((tx, ty), code, fill=text_color, font=font_grid)

    # 底部统计
    y_offset = output_size + 10
    x_offset = 10
    sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])
    for code, count in sorted_colors:
        color = palette.get(code, (200,200,200))
        draw.rectangle([x_offset, y_offset, x_offset+18, y_offset+18],
                       fill=rgb_to_hex(color), outline='#333333')
        text = f"{code}: {count}"
        draw.text((x_offset+22, y_offset), text, fill='#333333', font=font_stat)
        x_offset += 22 + len(text) * 9 + 15
        if x_offset > output_size - 50:
            x_offset = 10
            y_offset += 30

    return output_img, color_counts

# ================= Streamlit 界面 =================
st.set_page_config(page_title="拼豆图纸生成器", layout="wide")
st.title("🧩 拼豆图纸生成器")
st.markdown("上传图片，选择拼豆板尺寸，自动生成拼豆图纸和颜色清单")

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("📁 上传图片", type=["png", "jpg", "jpeg", "bmp", "gif"])
    grid_size = st.number_input("📐 拼豆板尺寸", min_value=10, max_value=200, value=52, step=1)
    scale = st.slider("🔍 输出清晰度（每格像素）", min_value=10, max_value=60, value=30, step=2)
    generate_btn = st.button("🎨 生成拼豆图", type="primary")

with col2:
    if uploaded_file is not None:
        st.image(uploaded_file, caption="原图预览", use_container_width=True)

if generate_btn and uploaded_file is not None:
    with st.spinner("🔄 正在生成拼豆图..."):
        img = Image.open(uploaded_file).convert('RGB')
        output_img, color_counts = image_to_perler(img, grid_size, PALETTE, scale=scale)

        st.success(f"✅ 生成完成！共需 {len(color_counts)} 种颜色，总计 {sum(color_counts.values())} 颗豆子")

        col_result, col_info = st.columns([2, 1])

        with col_result:
            st.image(output_img, caption="拼豆图纸", use_container_width=True)
            buf = io.BytesIO()
            output_img.save(buf, format="PNG", dpi=(300, 300))
            buf.seek(0)
            st.download_button(
                label="📥 下载高清图纸",
                data=buf,
                file_name=f"perler_{grid_size}x{grid_size}.png",
                mime="image/png"
            )

        with col_info:
            st.subheader("📊 所需颜色")
            total = sum(color_counts.values())
            for code, count in sorted(color_counts.items(), key=lambda x: -x[1]):
                color = PALETTE.get(code, (200,200,200))
                hex_code = rgb_to_hex(color)
                st.markdown(
                    f"<span style='display:inline-block;width:20px;height:20px;background:{hex_code};border:1px solid #ccc;border-radius:4px;'></span> "
                    f"**{code}** : {count} 颗 ({count/total*100:.1f}%)",
                    unsafe_allow_html=True
                )
