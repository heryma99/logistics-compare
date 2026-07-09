(function(){
  'use strict';
  // 访问密码的 SHA-256（小写十六进制）。密码: LogiView@2026
  // 修改密码：用 sha256(新密码) 替换下方 EXPECTED 即可。
  var EXPECTED = 'dd4f17d0395c2e94ff61a0239bdd614cf1c05af3fe3feb0e7d98f01a0d2a27b6';
  var LS_KEY = 'lc_gate_token';
  var TRIES_KEY = 'lc_gate_tries';
  var LOCK_KEY = 'lc_gate_lock';
  var MAX_TRIES = 5;
  var LOCK_MS = 5 * 60 * 1000;
  var body = document.body;

  function getLS(k){ try { return localStorage.getItem(k); } catch(e){ return null; } }
  function setLS(k,v){ try { localStorage.setItem(k,v); } catch(e){} }

  function sha256Hex(str){
    if(!window.crypto || !crypto.subtle){ return Promise.reject('no crypto'); }
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(str)).then(function(buf){
      return Array.prototype.map.call(new Uint8Array(buf), function(b){
        return ('0' + b.toString(16)).slice(-2);
      }).join('');
    });
  }

  // 同一浏览器已解锁过（同域共享）则直接放行
  if(getLS(LS_KEY) === EXPECTED){
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
        setLS(LS_KEY, EXPECTED);
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
