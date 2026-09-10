# -*- coding: utf-8 -*-
"""诊断 40164：打印微信 token 接口完整响应（errmsg 含微信实际看到的源 IP）。凭据只从文件读，不进命令行。"""
import json
import sys
import urllib.request

sys.path.insert(0, r"C:\Users\Administrator\.zcode\skills\wechat-publish\scripts")
import wx_token

secret = open(wx_token.SECRET_FILE, encoding="utf-8").read().strip()
url = (f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential"
       f"&appid={wx_token.APPID}&secret={secret}")
data = json.loads(urllib.request.urlopen(url, timeout=20).read().decode("utf-8"))
out = {"keys": list(data.keys())}
if "access_token" in data:
    out["result"] = "token OK"
else:
    out["errcode"] = data.get("errcode")
    out["errmsg"] = data.get("errmsg", "")
print(json.dumps(out, ensure_ascii=False, indent=2))
