import os
f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zhongyun_express.html')
s = open(f, encoding='utf-8').read()

# 1) 去掉之前误插到文件最开头的 HEAD_INJECT（恢复以 <!doctype 开头）
if not s.lstrip().lower().startswith('<!doctype'):
    i = s.lower().find('<!doctype')
    if i > 0:
        s = s[i:]

GATE_CSS = '''body.locked > *:not(#gate-overlay){display:none !important;}
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
.gate-foot{margin-top:16px;font-size:11px;color:#94a3b8;}'''

OVERLAY = '''<div id="gate-overlay">
  <div class="gate-box">
    <div class="gate-title">🔒 受限访问</div>
    <div class="gate-sub">跨境物流比价看板 · 请输入访问密码</div>
    <input id="gate-pwd" type="password" placeholder="访问密码" autocomplete="off" />
    <button id="gate-btn" type="button">进入看板</button>
    <div id="gate-err" class="gate-err"></div>
    <div class="gate-foot">密码请联系管理员获取</div>
  </div>
</div>'''

# 2) 补 <head> 开标签
s = s.replace('<html lang="zh-CN">', '<html lang="zh-CN"><head>', 1)
# 3) 在原始 </style> 之后插入 meta + gate css + </head> + body + overlay
s = s.replace('</style>', '</style>\n<meta name="robots" content="noindex, nofollow">\n<style>\n'
             + GATE_CSS + '\n</style>\n</head>\n<body class="locked">\n' + OVERLAY, 1)
# 4) gate.js 之前已注入在 </body> 前，确认存在
if 'gate.js' not in s:
    s = s.replace('</body>', '<script src="./gate.js"></script>\n</body>', 1)

open(f, 'w', encoding='utf-8').write(s)
print('fixed zhongyun_express.html')
