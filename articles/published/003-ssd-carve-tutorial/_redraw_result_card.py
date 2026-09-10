# -*- coding: utf-8 -*-
# 重画 003 成绩单卡：修复 265MB/s 与 75,759 两列粘连（2026-09-10 发布前 QA）
from PIL import Image, ImageDraw, ImageFont

MSYH = r"C:\Windows\Fonts\msyh.ttc"
MSYH_BD = r"C:\Windows\Fonts\msyhbd.ttc"
NAVY = (26, 35, 50)
GRID = (35, 48, 71)
GREEN = (74, 222, 128)
GRAY = (154, 167, 184)
RED = (248, 113, 113)
WHITE = (255, 255, 255)
HEADER_BG = (30, 41, 59)
TEXT = (203, 213, 225)

W, H = 900, 300
img = Image.new("RGB", (W, H), NAVY)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 52], fill=HEADER_BG)
d.text((28, 12), "27 分钟后的成绩单", font=ImageFont.truetype(MSYH_BD, 22), fill=WHITE)

cols = [
    ("430GB", "扫描体积", GREEN),
    ("≈265MB/s", "扫描速度", GREEN),
    ("75,759", "EOCD 候选", GREEN),
    ("1,103", "PDF 存档", GREEN),
    ("0", "zip 恢复", RED),
]
numfont = ImageFont.truetype(MSYH_BD, 36)
labfont = ImageFont.truetype(MSYH, 16)
gap = 38
widths = [max(numfont.getlength(n), labfont.getlength(l)) for n, l, _ in cols]
x = (W - (sum(widths) + gap * (len(cols) - 1))) / 2
for (num, lab, color), w in zip(cols, widths):
    d.text((x, 95), num, font=numfont, fill=color)
    d.text((x, 148), lab, font=labfont, fill=GRAY)
    x += w + gap

d.line([(45, 196), (W - 45, 196)], fill=GRID, width=1)
d.text((45, 216), "判决：SSD TRIM —— 删除指令发出后，操作系统通知 SSD 主控擦块。",
       font=ImageFont.truetype(MSYH, 16), fill=TEXT)
d.text((45, 248), "雕刻器读到的就是空白。这就是 0 的全部含义：物理销毁，软件层不可逆。",
       font=ImageFont.truetype(MSYH, 16), fill=TEXT)

out = r"D:\projects\project-experience-summary\articles\published\003-ssd-carve-tutorial\images\result_card.png"
img.save(out)
print("saved:", out)
