#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物流看板 自助改密码工具
=================================
用法（任选其一）：
  1) 双击本文件，按提示输入新密码（输入时不显示）。
  2) 命令行：  python change_password.py "你的新密码"
  3) 仍想让我帮你改：把新密码告诉我，我替你跑这一条。

流程：计算 SHA-256 -> 写入 gate.js -> git 提交并推送 -> GitHub Actions 自动重新部署（约30秒生效）。
"""
import hashlib
import os
import re
import subprocess
import sys


REPO = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(REPO, "gate.js")
REMOTE_HTTPS = "https://github.com/heryma99/logistics-compare.git"


def read_token():
    """从 ~/.git-credentials 读取 GitHub token（WorkBuddy 环境自带）。"""
    p = os.path.expanduser("~/.git-credentials")
    if os.path.exists(p):
        txt = open(p, encoding="utf-8", errors="ignore").read()
        m = re.search(r"https://([^@]+)@github", txt)
        if m:
            return m.group(1)
    return None


def get_password():
    if len(sys.argv) > 1:
        return sys.argv[1].strip()
    try:
        import getpass
        pw = getpass.getpass("请输入新密码（输入时不显示）：").strip()
    except Exception:
        pw = input("请输入新密码：").strip()
    return pw


def main():
    pw = get_password()
    if not pw:
        print("密码为空，已取消。")
        return 1

    digest = hashlib.sha256(pw.encode("utf-8")).hexdigest()

    if not os.path.exists(GATE):
        print(f"未找到 gate.js（应在 {GATE}），请确认脚本位置。")
        return 1

    src = open(GATE, encoding="utf-8").read()
    if "EXPECTED" not in src:
        print("gate.js 中未找到 EXPECTED 字段，可能结构已变，请联系维护。")
        return 1

    # 仅替换 var EXPECTED = '...' 赋值行（单/双引号皆可），保留原引号样式
    new_src = re.sub(
        r"(var\s+EXPECTED\s*=\s*['\"])[^'\"]*(['\"])",
        lambda m: m.group(1) + digest + m.group(2),
        src,
        count=1,
    )
    if new_src == src:
        print("注意：新密码哈希与当前一致，未做改动。")
    else:
        open(GATE, "w", encoding="utf-8").write(new_src)
        print("已更新 gate.js 密码哈希:", digest[:12], "...")

    # git 提交并推送
    subprocess.run(["git", "add", "gate.js"], cwd=REPO)
    res = subprocess.run(
        ["git", "-c", "core.quotepath=false", "commit", "-m", "chore: change dashboard password"],
        cwd=REPO,
    )
    if res.returncode != 0:
        print("（git commit 无变化或失败，跳过提交）")

    token = read_token()
    remote = f"https://{token}@github.com/heryma99/logistics-compare.git" if token else REMOTE_HTTPS
    r = subprocess.run(["git", "push", remote, "main"], cwd=REPO)
    if r.returncode == 0:
        print("已推送。GitHub Actions 会自动重新部署，约 30 秒后全站新密码生效。")
    else:
        print("推送失败，请检查网络或凭据；gate.js 已改好，可稍后手动 push。")
        return 1
    return 0


if __name__ == "__main__":
    rc = main()
    try:
        input("\n按回车关闭窗口...")
    except Exception:
        pass
    sys.exit(rc)
