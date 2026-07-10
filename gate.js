(function(){
  'use strict';
  // 访问密码的 SHA-256（小写十六进制）。密码: LogiView@2026
  // 修改密码：替换下方 EXPECTED，并把 PW_VERSION +1（旧会话因版本不符被强制重输 = 强制登出）。
  var EXPECTED = '29f2f5cabd600f22d328d42eccd19c7b2564fd4e952087710b98328a2fedb5dd';
  var PW_VERSION = 5;            // 每次改密码 +1；旧已登录会话版本不符 → 立即失效
  var LS_KEY = 'lc_gate_v1';
  var TRIES_KEY = 'lc_gate_tries';
  var LOCK_KEY = 'lc_gate_lock';
  var MAX_TRIES = 5;
  var LOCK_MS = 5 * 60 * 1000;
  var body = document.body;

  function getLS(k){ try { return localStorage.getItem(k); } catch(e){ return null; } }
  function setLS(k,v){ try { localStorage.setItem(k,v); } catch(e){} }
  function clearLS(){ try { localStorage.removeItem(LS_KEY); } catch(e){} }

  // 读取本地令牌：版本与哈希都匹配才视为已授权；否则清除（实现强制登出）
  function readToken(){
    try {
      var raw = getLS(LS_KEY);
      if(!raw) return null;
      var o = JSON.parse(raw);
      if(o && o.v === PW_VERSION && o.h === EXPECTED) return o;
    } catch(e){}
    clearLS();
    return null;
  }

  function sha256Hex(str){
    if(!window.crypto || !crypto.subtle){ return Promise.reject('no crypto'); }
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(str)).then(function(buf){
      return Array.prototype.map.call(new Uint8Array(buf), function(b){
        return ('0' + b.toString(16)).slice(-2);
      }).join('');
    });
  }

  // 已解锁过（同域共享）且版本匹配 → 直接放行
  if(readToken()){
    if(body) body.classList.remove('locked');
    return;
  }

  var ov = document.getElementById('gate-overlay');
  var pwd = document.getElementById('gate-pwd');
  var btn = document.getElementById('gate-btn');
  var errEl = document.getElementById('gate-err');

  function lockUI(){
    if(!ov) return;
    ov.innerHTML = '<div class="gate-box"><div class="gate-title">🔒 访问已锁定</div>' +
      '<div class="gate-msg">尝试次数过多，请 5 分钟后再试</div></div>';
  }
  function checkLock(){
    var until = parseInt(getLS(LOCK_KEY) || '0', 10);
    if(Date.now() < until){ lockUI(); return false; }
    return true;
  }
  if(!checkLock()){ return; }

  function unlock(){
    if(!checkLock()) return;
    var val = (pwd && pwd.value) || '';
    if(!val){ if(errEl) errEl.textContent = '请输入密码'; return; }
    sha256Hex(val).then(function(hex){
      if(hex === EXPECTED){
        setLS(LS_KEY, JSON.stringify({ v: PW_VERSION, h: EXPECTED }));
        setLS(TRIES_KEY, '0');
        if(body) body.classList.remove('locked');
        if(ov) ov.style.display = 'none';
      } else {
        var t = parseInt(getLS(TRIES_KEY) || '0', 10) + 1;
        setLS(TRIES_KEY, String(t));
        if(t >= MAX_TRIES){
          setLS(LOCK_KEY, String(Date.now() + LOCK_MS));
          lockUI();
          return;
        }
        if(errEl) errEl.textContent = '密码错误，还可尝试 ' + (MAX_TRIES - t) + ' 次';
        if(pwd){ pwd.value = ''; pwd.focus(); }
      }
    }).catch(function(){
      if(errEl) errEl.textContent = '当前浏览器不支持访问限制，请更换现代浏览器';
    });
  }

  if(btn) btn.addEventListener('click', unlock);
  if(pwd){
    pwd.focus();
    pwd.addEventListener('keydown', function(e){ if(e.key === 'Enter') unlock(); });
  }
})();
