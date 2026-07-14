(function(){
  'use strict';
  // 访问密码的 SHA-256（小写十六进制）。密码: LogiView@2026
  // 修改密码：替换下方 EXPECTED，并把 PW_VERSION +1（旧会话因版本不符被强制重输 = 强制登出）。
  var EXPECTED = 'a3cf67121e0481a98174c94884e8005863ca5edc93d20bf8a5eb565056e9aa37';
  var PW_VERSION = 6;            // 每次改密码 +1；旧已登录会话版本不符 → 立即失效
  var LS_KEY = 'lc_gate_v1';
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

  function unlock(){
    var val = (pwd && pwd.value) || '';
    if(!val){ if(errEl) errEl.textContent = '请输入密码'; return; }
    sha256Hex(val).then(function(hex){
      if(hex === EXPECTED){
        setLS(LS_KEY, JSON.stringify({ v: PW_VERSION, h: EXPECTED }));
        if(body) body.classList.remove('locked');
        if(ov) ov.style.display = 'none';
      } else {
        // 已关闭「多次错误锁定」：密码错误仅提示重试，不会计数或锁定
        if(errEl) errEl.textContent = '密码错误，请重试';
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
