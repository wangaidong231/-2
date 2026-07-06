import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from collections import Counter

# ================= 拼豆色卡 =================
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

# ================= 颜色距离 =================
def color_distance(c1, c2):
    return sum((c1[i] - c2[i]) ** 2 for i in range(3))

def find_closest_color(rgb):
    best = None
    best_d = 1e18
    for k, v in PALETTE.items():
        d = color_distance(rgb, v)
        if d < best_d:
            best_d = d
            best = k
    return best

# ================= 核心转换 =================
def convert(img, grid_size, scale):
    img = img.convert("RGB")

    w, h = img.size
    aspect = w / h

    if aspect > 1:
        new_w = grid_size
        new_h = int(grid_size / aspect)
    else:
        new_h = grid_size
        new_w = int(grid_size * aspect)

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    arr = np.array(img)

    grid = []
    counter = Counter()

    for i in range(new_h):
        row = []
        for j in range(new_w):
            code = find_closest_color(arr[i, j])
            row.append(code)
            counter[code] += 1
        grid.append(row)

    out_size = grid_size * scale
    out = Image.new("RGB", (out_size, out_size), "white")
    draw = ImageDraw.Draw(out)

    try:
        font = ImageFont.truetype("arial.ttf", max(8, scale // 3))
    except:
        font = ImageFont.load_default()

    for i in range(new_h):
        for j in range(new_w):
            code = grid[i][j]
            color = PALETTE[code]

            x0, y0 = j * scale, i * scale
            x1, y1 = x0 + scale, y0 + scale

            draw.rectangle([x0, y0, x1, y1], fill=color, outline="#ddd")

            if scale >= 12:
                draw.text((x0+3, y0+3), code, fill="black", font=font)

    return out, counter

# ================= Streamlit UI =================
st.set_page_config(page_title="拼豆生成器", layout="wide")

st.title("🧩 拼豆图纸生成器（Streamlit版）")

uploaded = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])

grid_size = st.slider("拼豆尺寸", 20, 120, 60)
scale = st.slider("清晰度", 10, 50, 25)

if uploaded:
    img = Image.open(uploaded)

    col1, col2 = st.columns(2)

    with col1:
        st.image(img, caption="原图", use_container_width=True)

    if st.button("生成拼豆图"):
        result, counter = convert(img, grid_size, scale)

        with col2:
            st.image(result, caption="拼豆图", use_container_width=True)

        st.subheader("颜色统计")

        total = sum(counter.values())

        for k, v in counter.most_common():
            col = PALETTE[k]
            hexv = '#%02x%02x%02x' % col
            st.markdown(
                f"<span style='background:{hexv};padding:4px 10px;border-radius:5px'>{k}</span> "
                f"{v} ({v/total*100:.1f}%)",
                unsafe_allow_html=True
            )
