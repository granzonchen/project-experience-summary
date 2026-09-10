# -*- coding: utf-8 -*-
"""带重试的建草稿：40164 白名单生效延迟时每 30s 重试（最多 6 次），token 通过即自动完成素材上传+建草稿+验证。"""
import subprocess
import sys
import time

sys.path.insert(0, r"D:\projects\project-experience-summary\articles\published\003-ssd-carve-tutorial")

MAX_RETRY = 6
WAIT = 30

for attempt in range(1, MAX_RETRY + 1):
    print(f"=== attempt {attempt}/{MAX_RETRY} ===", flush=True)
    # 先单独试 token，避免素材重复上传
    r = subprocess.run(
        [sys.executable,
         r"D:\projects\project-experience-summary\articles\published\003-ssd-carve-tutorial\_diag_ip.py"],
        capture_output=True, text=True, encoding="utf-8")
    if '"result": "token OK"' in r.stdout:
        print("token OK, running full draft build...", flush=True)
        import _build_draft_003 as b
        b.main()
        print("=== DONE ===", flush=True)
        break
    print("token not ready yet:", "40164" in r.stdout and "40164 still" or r.stdout[-200:], flush=True)
    if attempt < MAX_RETRY:
        time.sleep(WAIT)
else:
    print("=== FAILED: 白名单仍未生效（3 分钟内 6 次重试均 40164）===", flush=True)
