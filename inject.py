import os, re, glob

REPO = os.path.dirname(os.path.abspath(__file__))
HTMLS = sorted(glob.glob(os.path.join(REPO, '*.html')))

HEAD_INJECT = '''<meta name="robots" content="noindex, nofollow">
<style>
body.locked > *:not(#gate-overlay){display:none !important;}
#gate-overlay{position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0f172a,#1e293b);font-family:-apple-system,"Microsoft YaHei",sans-serif;}
body:not(.locked) #gate-overlay{display:none !important;}
.gate-box{background:#fff;border-radius:16px;padding:34px 38px;width:330px;max-width:90vw;box-shadow:0 24px 70px rgba(0,0,0,.5);text-align:center;}
.gate-title{font-size:21px;font-weight:800;color:#0f172a;margin-bottom:6px;}
.gate-sub{font-size:13px;color:#64748b;margin-bottom:20px;}
#gate-pwd{width:100%;box-sizing:border-box;padding:12px 14px;border:1.5px solid #cbd5e1;border-radius:10px;font-size:15px;outline:none;transition:border-color .15s;}
#gate-pwd:focus{border-color:#2563eb;}
#gate-btn{margin-top:16px;width:100%;padding:12px;border:none;border-radius:10px;background:#2563eb;color:#fff;font-size:15px;font-weight:700;cursor:pointer;transition:background .15s;}
#gate-btn:hover{background:#1d4ed8;}
.gate-err{color:#dc2626;font-size:12.5px;margin-top:12px;min-height:16px;}
.gate-foot{margin-top:16px;font-size:11px;color:#94a3b8;}
</style>
'''

OVERLAY = '''<div id="gate-overlay">
  <div class="gate-box">
    <div class="gate-title">🔒 受限访问</div>
    <div class="gate-sub">跨境物流比价看板 · 请输入访问密码</div>
    <input id="gate-pwd" type="password" placeholder="访问密码" autocomplete="off" />
    <button id="gate-btn" type="button">进入看板</button>
    <div id="gate-err" class="gate-err"></div>
    <div class="gate-foot">密码请联系管理员获取</div>
  </div>
</div>
'''

SCRIPT = '<script src="./gate.js"></script>\n'

patched = 0
for f in HTMLS:
    s = open(f, encoding='utf-8').read()
    if 'id="gate-overlay"' in s or 'gate.js' in s:
        print('SKIP (already patched):', os.path.basename(f))
        continue
    # 1) head: 注入 noindex + gate 样式
    if '</head>' in s:
        s = s.replace('</head>', HEAD_INJECT + '</head>', 1)
    else:
        m = re.search(r'<head[^>]*>', s, re.I)
        if m:
            s = s[:m.end()] + HEAD_INJECT + s[m.end():]
        else:
            s = HEAD_INJECT + s
    # 2) body 标签加 class="locked"
    def body_class(m):
        tag = m.group(0)
        if 'class=' in tag:
            return re.sub(r'class="([^"]*)"', lambda x: 'class="' + x.group(1) + ' locked"', tag, count=1)
        return tag.replace('>', ' class="locked">', 1)
    s = re.sub(r'<body[^>]*>', body_class, s, count=1, flags=re.I)
    # 3) body 标签后注入 overlay
    s = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + '\n' + OVERLAY, s, count=1, flags=re.I)
    # 4) </body> 前注入 gate.js
    if '</body>' in s:
        s = s.replace('</body>', SCRIPT + '</body>', 1)
    else:
        s = s + '\n' + SCRIPT
    open(f, 'w', encoding='utf-8').write(s)
    patched += 1
    print('PATCHED:', os.path.basename(f))

print('--- done, patched', patched, 'files ---')
