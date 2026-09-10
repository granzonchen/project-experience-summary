# -*- coding: utf-8 -*-
"""获取 003 发布后的正式 /s/ 链接：freepublish/batchget 列出已发表文章。凭据只从文件读。"""
import json
import sys
import urllib.request

sys.path.insert(0, r"C:\Users\Administrator\.zcode\skills\wechat-publish\scripts")
from wx_token import get_token

token = get_token()
url = f"https://api.weixin.qq.com/cgi-bin/freepublish/batchget?access_token={token}"
payload = json.dumps({"offset": 0, "count": 5, "no_content": 1}).encode("utf-8")
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))

if "item" not in data:
    print(json.dumps({"errcode": data.get("errcode"), "errmsg": data.get("errmsg", "")[:120]}, ensure_ascii=False))
else:
    for it in data.get("item", []):
        for art in it.get("content", {}).get("news_item", []):
            print(json.dumps({"title": art.get("title"), "url": art.get("url"),
                              "update_time": it.get("update_time")}, ensure_ascii=False))
