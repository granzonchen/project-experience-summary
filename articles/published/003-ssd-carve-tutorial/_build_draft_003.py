# -*- coding: utf-8 -*-
"""003 路线 A：上传素材 + 建草稿（A+C 定版形态的 A 半；发布按钮仍留给人）。

产物：微信草稿箱 1 篇（标题/摘要/封面/4 图/样式正文）。
验证：draft/add 的 media_id → draft/get 拉回核对标题、digest、img 数量。
"""
import json
import os
import sys
import uuid
import urllib.request

SKILL_SCRIPTS = r"C:\Users\Administrator\.zcode\skills\wechat-publish\scripts"
sys.path.insert(0, SKILL_SCRIPTS)
from wx_token import get_token

IMG_DIR = r"D:\projects\project-experience-summary\articles\published\003-ssd-carve-tutorial\images"
TITLE = "SSD 上删掉的文件还能救吗？我用 200 行 Python 扫了 430GB 找答案"
DIGEST = ("上一篇讲到删库后四路恢复全败。这一篇把第四路展开：为什么现成工具全哑火、"
          "手写雕刻器需要的三个 Windows API 知识点、EOCD 反向重组的原理，以及 430GB 扫描给出的最终答案。")

P_STYLE = 'font-size:17px;line-height:1.75;color:#333;margin:0 0 16px 0;letter-spacing:0.3px;'
H2_STYLE = ('font-size:18px;font-weight:bold;color:#1a1a1a;'
            'border-left:4px solid #1d78c9;padding-left:12px;margin:34px 0 18px;')
CAP_STYLE = 'text-align:center;color:#999;font-size:13px;margin:0 0 22px;'
QUOTE_STYLE = ('background:#f7f7f7;border-left:3px solid #d0d0d0;padding:12px 16px;'
               'color:#666;font-size:15px;line-height:1.7;margin:26px 0;')
BLUE_STYLE = 'color:#1d78c9;font-weight:bold;font-size:16px;line-height:1.7;margin:30px 0 16px;'
CENTER_STYLE = 'text-align:center;color:#888;font-size:14px;margin:26px 0;'
SMALL_STYLE = 'color:#aaa;font-size:12px;margin-top:28px;'


def md_inline(t):
    parts = t.split("**")
    return "".join(f"<strong>{p}</strong>" if i % 2 == 1 else p for i, p in enumerate(parts))


def api_post_json(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def upload_image(token, path):
    boundary = "----wx" + uuid.uuid4().hex
    body = bytearray()
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"media\"; "
             f"filename=\"{os.path.basename(path)}\"\r\nContent-Type: image/png\r\n\r\n").encode("ascii")
    body += open(path, "rb").read()
    body += f"\r\n--{boundary}--\r\n".encode("ascii")
    req = urllib.request.Request(
        f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def build_content(imgs):
    e = []  # (kind, *args)

    def P(t):
        e.append(("p", t))

    def H2(t):
        e.append(("h2", t))

    def IMG(name, caption):
        e.append(("img", name, caption))

    P("上一篇《AI 替我删库翻车实录》的结尾，三个目录被误删，四路恢复全败。悬而未决的问题是：**SSD 上删掉的文件，真的救不回来吗？**")
    P("这篇把第四路——自研磁盘雕刻器——完整展开。200 行 Python，扫了 430GB，27 分钟。答案是一个 0。但这个 0 的得出过程，比结论本身值钱。")
    H2("01 为什么现成工具全哑火")
    IMG("routes_card", "四路恢复战绩")
    P("三个工具的死法各有代表性：")
    P("**winfr** 没装上——商店分发在你控制不了的环境里随时会卡死。")
    P(r"**pytsk3** 装上了，但 Windows 轮子打不开原始卷——\\.\D: 各种写法全部报错，开源取证库对 Windows 的支持是二等公民。")
    P("**PhotoRec 的三个坑最值得展开**：①二进制带 requireAdministrator 清单，从非提权会话启动是**静默退出**——没有报错、没有日志，进程号都有了然后没了；②提权之后命令行的设备名不认盘符，D: 会被当成普通文件路径去 stat（“Unable to open file or device D:”）；③交互模式配输出重定向，curses 界面往重定向里刷了 5GB 转义序列。")
    P("**教训：提权类工具的失败是静默的。**想让它的输出可见，唯一的办法是输出重定向 + 独立日志文件，外加一个随时可读的状态文件。")
    H2("02 开工前必须知道的三个 API 事实")
    P("自己写的第一版一秒就结束了——因为卷大小查出来是 0。修好之后才明白，Windows 原始卷编程有三个和普通文件完全不同的规矩：")
    P(r"**一、打开原始卷要用 CreateFileW，并且要管理员。**\\.\D: 这种设备路径，GENERIC_READ 加上 FILE_SHARE_READ | FILE_SHARE_WRITE 的共享标志——共享标志给错，句柄打开就会挂起或被拒。")
    P("**二、定位读要用 ReadFile + OVERLAPPED 结构。**卷句柄不是普通文件句柄，文件指针那套 API 不好使；偏移量拆成 Offset / OffsetHigh 塞进 OVERLAPPED。而且原始卷读要求**偏移和长度都按扇区对齐**——这是我用“16 字节探测读永远返回 None”换来的一课。")
    P("**三、卷大小别用 GetFileSizeEx 查。**对卷句柄它返回 0。正确姿势是 GetDiskFreeSpaceExW 的“总容量”字段——已用加可用，正好等于卷容量。")
    H2("03 雕刻逻辑：三类特征 + 一个反向重组")
    P("扫描循环很朴素：8MB 一块滚动读，块间留 4MB 重叠（防止特征恰好跨在块边界上漏检），在缓冲区里找三类特征——zip 本地头、zip 的 EOCD 结尾标记、PDF 的 %PDF-。")
    P("真正的巧思在 zip 的重组上。zip 文件的结构是固定的：")
    IMG("eocd_principle_card", "EOCD 反向定位法")
    P("EOCD（End of Central Directory）结构里存着中央目录的偏移和长度。所以不需要从头解析——**从任何一个 EOCD 候选反向回推**：zip 起点 = EOCD 位置 - cd_size - cd_offset，验证起点 4 字节是不是 PK 头，是就按长度把整段字节切出来，一个完整的 zip 文件就还原了。")
    P("PDF 更简单：%PDF- 起步，60MB 窗口内找 %%EOF 截断。")
    P("噪声过滤加一条硬规则：**小于 1MB 的 zip 全部丢弃**——在 node_modules 时代，盘上的碎片 zip 多到怀疑人生。")
    H2("04 我踩的三个坑")
    IMG("pitfalls_card", "我踩的三个坑")
    P("每个坑都值一条铁律：")
    P("**GetFileSizeEx 对卷句柄返回 0**——卷不是文件。症状是脚本一秒结束、卷大小 0.0GB，扫描循环根本没进。")
    P("**非对齐探测读永远 None**——“probe=None，怀疑人生”。原始卷读的对齐纪律：偏移、长度、缓冲区，三个都要对齐扇区。")
    P("**提权隐藏窗口里的静默死亡**——字符串补丁误删了一个类定义，NameError 抛在了一个没有控制台的隐藏提权窗口里，无人看见。药方是笨办法但唯一有效：**状态文件秒写**（每一步先把“我到哪了”写进文件）+ 全量异常捕获落盘。")
    H2("05 27 分钟后的答案")
    IMG("result_card", "27 分钟后的成绩单")
    P("430GB，约 265MB/s，扫描+重组 27 分钟。EOCD 候选七万五千多个，PDF 存档 1103 个，**zip 恢复：0**。")
    P("这个 0 是 TRIM 的判决书：删除指令发出后，操作系统通知 SSD 主控擦块，雕刻器读到的就是空白。上篇的结论在这里拿到了物理层的实证——**SSD 上删除即销毁，恢复窗口在删除之前**。")
    H2("06 完整脚本与三条使用红线")
    P("完整脚本约 200 行，公众号后台回复「**雕刻器**」获取。三条红线先立好：")
    P("**只扫自己的盘**——原始卷读取是取证级操作，对别人的盘做就是另一回事了。")
    P("**恢复输出写到另一块物理盘**——往源盘写等于一边捞一边埋。")
    P("**记住 TRIM 窗口期**——删除后越早扫越有戏，写盘越多越没戏。以及最重要的心理预期：在 SSD 上，这个工具最大的用途不是“找回数据”，而是**出具“数据已物理销毁”的判决书**——本次事故里，正是这个 0 让我彻底死心，也彻底认清了铁律。")
    H2("写在最后")
    P("四路恢复里，最“笨”的一路给出了最确定的答案。现成工具给不了确定性的地方，往往是“读原始字节 + 理解文件格式”这种笨功夫的领地。")
    P("以及一个诚实的补充：这次雕刻的对象是我自己的盘、我自己的数据。同样的技术在错误的用途上就是另一回事——**工具没有立场，持刀的人有**。")

    html = []
    for item in e:
        kind = item[0]
        if kind == "p":
            html.append(f'<p style="{P_STYLE}">{md_inline(item[1])}</p>')
        elif kind == "h2":
            html.append(f'<h2 style="{H2_STYLE}">{item[1]}</h2>')
        elif kind == "img":
            name, caption = item[1], item[2]
            url = imgs[name]["url"]
            html.append(f'<img src="{url}" style="width:100%;height:auto;display:block;margin:10px 0 6px;" data-ratio="0.333" data-w="900"/>')
            html.append(f'<p style="{CAP_STYLE}">▲ {caption}</p>')

    html.append(f'<blockquote style="{QUOTE_STYLE}">你有没有过“删了才想起没备份”的时刻？后台回复「铁律」，拿走当前全部工程铁律清单。</blockquote>')
    html.append(f'<p style="{BLUE_STYLE}">欢迎回到试验田，这是田里的第 3 个故事——一个 0 结果的故事，也可能是最值钱的一个。</p>')
    html.append(f'<p style="{CENTER_STYLE}">—— 试验田 · 第 3 篇 ——</p>')
    html.append(f'<p style="{SMALL_STYLE}"><em>本文基于作者真实经历，代码经实际运行验证，由 AI 辅助整理。</em></p>')
    return "".join(html)


def main():
    token = get_token()
    print("token ok")
    imgs = {}
    for name in ["routes_card", "eocd_principle_card", "pitfalls_card", "result_card"]:
        r = upload_image(token, os.path.join(IMG_DIR, name + ".png"))
        if "media_id" not in r:
            raise SystemExit(f"上传失败 {name}: {r}")
        imgs[name] = r
        print(f"uploaded {name}: url={'yes' if r.get('url') else 'NO'}")
    cover = upload_image(token, os.path.join(IMG_DIR, "cover_900x383.png"))
    if "media_id" not in cover:
        raise SystemExit(f"封面上传失败: {cover}")
    print("uploaded cover")

    content = build_content(imgs)
    payload = {"articles": [{
        "title": TITLE,
        "author": "试验田",
        "digest": DIGEST,
        "content": content,
        "thumb_media_id": cover["media_id"],
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }]}
    r = api_post_json(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", payload)
    if "media_id" not in r:
        raise SystemExit(f"draft/add 失败: {r}")
    print(f"draft created: {r['media_id']}")

    chk = api_post_json(f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}",
                        {"media_id": r["media_id"]})
    art = chk["news_item"][0]
    print(f"verify: title={art['title'][:20]}... digest_len={len(art['digest'])} "
          f"img_count={art['content'].count('<img')} content_len={len(art['content'])}")


if __name__ == "__main__":
    main()
