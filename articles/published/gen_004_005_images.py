# -*- coding: utf-8 -*-
"""生成 004/005 两篇公众号配图：2 封面 + 5 图卡（复刻 003 视觉规范）"""
from PIL import Image, ImageDraw, ImageFont
import os

MSYH = r"C:\Windows\Fonts\msyh.ttc"
MSYH_BD = r"C:\Windows\Fonts\msyhbd.ttc"
CONSOLA = r"C:\Windows\Fonts\consola.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

NAVY = (26, 35, 50)
GRID = (35, 48, 71)
GREEN = (74, 222, 128)
GRAY = (154, 167, 184)
RED = (248, 113, 113)
WHITE = (255, 255, 255)
ORANGE = (234, 88, 12)
BLUE = (29, 78, 216)
CARD_BG = (243, 244, 246)
TEXT_DARK = (31, 41, 55)
TEXT_GRAY = (75, 85, 99)
HEADER_BG = (30, 41, 59)

def cover(path, article_no, kind, title, subtitle, lines, footer):
    W, H = 900, 383
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 45):
        d.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, 45):
        d.line([(0, y), (W, y)], fill=GRID, width=1)
    d.text((50, 48), title, font=F(MSYH_BD, 38), fill=WHITE)
    d.text((50, 108), subtitle, font=F(MSYH_BD, 24), fill=GREEN)
    y = 175
    for text, color in lines:
        d.text((50, y), text, font=F(CONSOLA, 21), fill=color)
        y += 42
    d.line([(50, H - 45), (W - 50, H - 45)], fill=GRID, width=1)
    d.text((50, H - 36), footer, font=F(MSYH, 15), fill=GRAY)
    img.save(path)

def card(path, header, items, H=560):
    """items: list of (序号, 蓝色标题, 灰色描述1, 橙色补充)"""
    W = 900
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 62], fill=HEADER_BG)
    d.text((28, 16), header, font=F(MSYH_BD, 24), fill=WHITE)
    y = 86
    n = len(items)
    ch = (H - 86 - 20 * (n + 1)) // n
    for i, (num, t, d1, d2) in enumerate(items):
        top = y + i * (ch + 20)
        d.rounded_rectangle([24, top, W - 24, top + ch], radius=10, fill=CARD_BG)
        cx, cy = 52, top + ch // 2
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=ORANGE)
        d.text((cx, cy - 13), str(num), font=F(MSYH_BD, 18), fill=WHITE, anchor="mm")
        d.text((86, top + 16), t, font=F(MSYH_BD, 21), fill=BLUE)
        d.text((86, top + 52), d1, font=F(MSYH, 16), fill=TEXT_DARK)
        if d2:
            d.text((86, top + 80), d2, font=F(MSYH, 15), fill=ORANGE)
    img.save(path)

B4 = r"D:\projects\project-experience-summary\articles\published\004-退役终点站\images"
B5 = r"D:\projects\project-experience-summary\articles\published\005-瘦身实录\images"

# ── 004 封面 ──
cover(os.path.join(B4, "cover_900x383.png"), 4, "tech",
      "33 个项目的退役终点站",
      "归档不是塞进文件夹就完事",
      [("$ ls projects-old   # 23 dirs  4.0GB", GRAY),
       ("compact=19  sha256=ALL-PASS  freed=1.4GB", GREEN),
       ("lost_account -> snapshot-commit -> own-repo", RED)],
      "试验田 · 第 4 篇 · 技术配方")

# ── 004 卡 1：两层终态形态 ──
card(os.path.join(B4, "architecture_card.png"), "终态形态：只留两层，每项目三选一", [
    ("1", "治理文档区（说明书）", "清点清单 / 脱敏记录 / SHA256 账本 / 总索引", "原则：宁保守，勿整洁"),
    ("2", "压缩归档区（藏书）", "每项目一个 7z + 一份 SHA256 签名，git 历史连包保留", "恢复 = 解包即得原目录"),
    ("3", "三选一：压缩 / 保持 / 删除", "逐项表态，\"以后再说\"是归档地膨胀的根因", "删除只走回收站，禁直删"),
], H=470)

# ── 004 卡 2：批次纪律 ──
card(os.path.join(B4, "batch_card.png"), "批次纪律：试点 → 中型 → 大型", [
    ("1", "打包：py7zr 逐单元 7z", "35M 试点走通流程 → 750M 中型 → 3.3G 大型，每批单独拍板", ""),
    ("2", "金标准校验", "完整解压 + 逐文件 SHA256 比对，全对才允许删源", "校验不过，绝不删"),
    ("3", "记账 + 回收站", "体积/SHA256/源目录写 MANIFEST；源进回收站且不清空", "移动归档后还要再复核一遍"),
], H=440)

# ── 004 卡 3：单一根 ──
card(os.path.join(B4, "index_card.png"), "归档最怕的不是大，是散", [
    ("1", "两个根的教训", "想看归档全貌，发现 2.6GB 主力包在另一处——连自己都找不齐", ""),
    ("2", "单一根 + 总索引", "一个 md 写清每个子目录是什么/多大/怎么恢复，30 秒定位", ""),
    ("3", "移动后必须复核", "重算每包 SHA256 对清单：24 文件/26 亿字节逐位一致才算完成", "复制完成 ≠ 移动完成"),
], H=440)

# ── 005 封面 ──
cover(os.path.join(B5, "cover_900x383.png"), 5, "story",
      "删掉 7GB 之后，回收站先背刺了我",
      "两轮瘦身战役的三个脏现场",
      [("$ purge --workspace=projects-old,vuefront", GRAY),
       ("freed=7GB  packs=19  sha256=ALL-PASS", GREEN),
       ("fifo_evicted=3.1GB  # silently dropped", RED)],
      "试验田 · 第 5 篇 · 实录")

# ── 005 卡 1：数字战报 ──
card(os.path.join(B5, "battle_card.png"), "诚实的战报：压缩几乎不省体积", [
    ("1", "projects-old：4045MB → 2595MB", "19 个压缩包占 2.6GB，正中开工前预估区间 2.2~2.7GB", ""),
    ("2", "vue_front_project：3345MB → 145MB", "72% 是 node_modules——可重建物，删了不算本事", ""),
    ("3", "收益不是省磁盘", "git pack 自带压缩，.git 占一半体积只挤得动 5~15%", "把频繁打扰折叠成安静确定性"),
], H=470)

# ── 005 卡 2：FIFO 背刺 ──
card(os.path.join(B5, "fifo_card.png"), "回收站的先进先出背刺", [
    ("1", "对账发现：3.1GB 原件不在站里", "回收站有配额（本机约 4GB），满了按先进先出静默淘汰", "无提示 / 无日志 / 无交互"),
    ("2", "\"进了回收站=安全\"是错觉", "它是一个有容量上限的延迟删除队列，不是备份", ""),
    ("3", "正确顺序", "归档 → 校验 → 删除 → 对账 → 清空，跳步=延迟的后悔", "淘汰无损失的前提：归档先行"),
], H=470)

# ── 005 卡 3：删除四铁律 ──
card(os.path.join(B5, "rules_card.png"), "删除四铁律", [
    ("1", "回收站不是备份", "有配额的延迟删除队列，先进先出，静默淘汰", ""),
    ("2", "删除成功 = 曾经存在 + 现在不在", "只验证后一半的守卫，会把\"没找到\"当\"已删除\"", ""),
    ("3", "金标准校验先行", "完整解压 + 逐文件 SHA256 全对才删源；移动后再对一遍", ""),
    ("4", "对账发生在清空前", "清空不可逆，对账是最后的止损窗口", ""),
], H=560)

print("generated:")
ROOT = "D:/projects/project-experience-summary/"
for b in (B4, B5):
    for f in sorted(os.listdir(b)):
        print(" ", os.path.join(b, f).replace("\\", "/").replace(ROOT, ""), os.path.getsize(os.path.join(b, f)) // 1024, "KB")
