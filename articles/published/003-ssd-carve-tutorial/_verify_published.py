# -*- coding: utf-8 -*-
"""003 线上终检：标题/摘要/小标题/加粗/收口模板/AI 声明/图片 fetch 逐项核验。

方法：/s/ 链接全文 HTML → js_content 区域解析；图片按 data-src 逐张 fetch 验 200；
文本断言用「去空白归一化」匹配，规避编辑器分段 span 造成的空白。
"""
import json
import re
import urllib.request

URL = "https://mp.weixin.qq.com/s/fafepbhiTVGc9izRvA1aQw"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.42")

req = urllib.request.Request(URL, headers={"User-Agent": UA})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

start = html.find('id="js_content"')
end = html.find('id="js_tags"')
if end == -1 or end < start:
    end = html.find('id="js_profile_qrcode"')
if end == -1 or end < start:
    end = len(html)
region = html[start:end] if start != -1 else ""

norm = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", region))

results = {}

m = re.search(r'property="og:title" content="([^"]*)"', html)
title = m.group(1) if m else ""
results["标题"] = ("PASS" if re.sub(r"\s+", "", title) ==
                "SSD上删掉的文件还能救吗？我用200行Python扫了430GB找答案" else f"FAIL: {title}")

m = re.search(r'property="og:description" content="([^"]*)"', html)
digest = m.group(1) if m else ""
results["摘要"] = ("PASS" if "四路恢复全败" in digest and "430GB" in digest else f"FAIL: {digest[:60]}")

sections = ["01为什么现成工具全哑火", "02开工前必须知道的三个API事实",
            "03雕刻逻辑：三类特征+一个反向重组", "04我踩的三个坑",
            "0527分钟后的答案", "06完整脚本与三条使用红线", "写在最后"]
missing = [s for s in sections if s not in norm]
results["7个小标题"] = "PASS" if not missing else f"FAIL 缺: {missing}"

strong_n = len(re.findall(r"<strong", region))
results["加粗strong数"] = f"{'PASS' if strong_n >= 21 else 'WARN'}: {strong_n}（样式表 21 处）"

tailings = {
    "开篇问句": "SSD上删掉的文件，真的救不回来吗？",
    "互动句": "你有没有过“删了才想起没备份”的时刻？后台回复「铁律」，拿走当前全部工程铁律清单。",
    "蓝色尾句": "欢迎回到试验田，这是田里的第3个故事——一个0结果的故事，也可能是最值钱的一个。",
    "系列落款": "——试验田·第3篇——",
    "AI小字": "本文基于作者真实经历，代码经实际运行验证，由AI辅助整理。",
    "雕刻器钩子": "后台回复「雕刻器」获取",
}
for name, s in tailings.items():
    results[name] = "PASS" if re.sub(r"\s+", "", s) in norm else "FAIL"

results["blockquote互动灰框"] = "PASS" if "<blockquote" in region else "FAIL"
results["AI生成声明"] = "PASS" if "内容由AI生成" in html else "FAIL"
results["原创标"] = f"{'PASS' if html.count('原创') >= 1 else 'FAIL'}: DOM 中「原创」出现 {html.count('原创')} 处（002 基线=1）"

residue = [r for r in ["**", "〔小标题〕", "【插图"] if r in norm]
results["markdown残留"] = "PASS" if not residue else f"FAIL: {residue}"

imgs = [u for u in re.findall(r'data-src="([^"]+)"', region)
        if u.startswith("https://") and "qpic.cn" in u]
img_report = []
for i, u in enumerate(imgs, 1):
    try:
        r2 = urllib.request.Request(u, headers={"User-Agent": UA})
        resp = urllib.request.urlopen(r2, timeout=20)
        img_report.append(f"图{i}: {resp.status} {resp.headers.get('Content-Type')}")
    except Exception as exc:
        img_report.append(f"图{i}: FAIL {exc}")
results["图片fetch"] = f"{len(imgs)} 张 | " + " | ".join(img_report)

print(json.dumps(results, ensure_ascii=False, indent=2))
