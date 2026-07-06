import numpy as np
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
import os
import tkinter as tk
from tkinter import filedialog, simpledialog

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

def load_image():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="选择要转换的图片",
        filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )

def get_grid_size():
    root = tk.Tk()
    root.withdraw()
    return simpledialog.askinteger(
        "选择拼豆板尺寸",
        "请输入拼豆板尺寸（如 52 或 104）：\n建议范围：30-200",
        minvalue=10, maxvalue=500, initialvalue=52
    )

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

def image_to_perler(img_path, grid_size, palette, show_text=True,
                    text_size_ratio=0.35, bg_color=(240,240,240),
                    scale=30):  # 🔺 清晰度提高：每个格子像素从20提高到30
    """
    将图片转换为拼豆图（保持宽高比，居中放置）
    参数：
        scale: 每个格子的像素大小（默认30，增大可提高输出清晰度）
    """
    img = Image.open(img_path).convert('RGB')
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

    canvas = Image.new('RGB', (grid_size, grid_size), bg_color)
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
        font_stat = ImageFont.truetype("arial.ttf", 16)  # 统计字体加大
    except:
        font_stat = ImageFont.load_default()
    font_size = max(6, int(scale * text_size_ratio))
    try:
        font_grid = ImageFont.truetype("arial.ttf", font_size)
    except:
        font_grid = ImageFont.load_default()

    for i in range(grid_size):
        for j in range(grid_size):
            code = perler_grid[i][j]
            color = palette.get(code, (200,200,200))
            x0 = j * scale
            y0 = i * scale
            x1 = x0 + scale
            y1 = y0 + scale
            draw.rectangle([x0, y0, x1, y1], fill=rgb_to_hex(color), outline='#cccccc')
            if show_text and scale >= 10:
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

    return perler_grid, color_counts, output_img

def main():
    print("="*50)
    print("🟢 拼豆图纸生成器（高清晰度版）")
    print("="*50)

    img_path = load_image()
    if not img_path:
        print("❌ 未选择图片")
        return
    print(f"✅ 已选择: {os.path.basename(img_path)}")

    grid_size = get_grid_size()
    if not grid_size:
        print("❌ 未输入尺寸")
        return
    print(f"✅ 尺寸: {grid_size}×{grid_size}")

    # 清晰度控制：每个格子的像素数（默认30，可在此处修改）
    SCALE = 30   # 🔺 调高到40可获得更清晰输出，但文件会更大
    print(f"🔍 每个格子放大 {SCALE} 像素，输出总尺寸约 {grid_size*SCALE}×{grid_size*SCALE}")

    print("\n🔄 正在转换 (保持比例，居中留白)...")
    grid, counts, output_img = image_to_perler(
        img_path, grid_size, PALETTE,
        show_text=True,
        text_size_ratio=0.35,
        bg_color=(240,240,240),
        scale=SCALE
    )

    base_name = os.path.splitext(os.path.basename(img_path))[0]
    output_path = f"{base_name}_perler_{grid_size}x{grid_size}_hd.png"
    # 保存时嵌入300 DPI，提升打印清晰度
    output_img.save(output_path, dpi=(300, 300))
    print(f"✅ 已保存高清图: {output_path}")

    print("\n📊 所需颜色统计:")
    total = sum(counts.values())
    for code, count in sorted(counts.items(), key=lambda x: -x[1]):
        hex_code = rgb_to_hex(PALETTE.get(code, (200,200,200)))
        print(f"  {code}  {hex_code}  →  {count} 颗 ({count/total*100:.1f}%)")

    print("\n" + "="*50)
    print(f"🎉 完成！共需 {len(counts)} 种颜色，总计 {total} 颗")
    print(f"📄 高清图纸: {output_path}")
    print("="*50)

    output_img.show()

if __name__ == "__main__":
    main()