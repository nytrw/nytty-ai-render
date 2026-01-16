from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from cerebras.cloud.sdk import Cerebras
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---- Cerebras client ----
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY")
client = Cerebras(api_key=CEREBRAS_API_KEY)

# ---- Usage tracking ----
usage = {}  # { user_id: {"count": 0, "date": "YYYY-MM-DD"} }
DAILY_LIMIT = 10

def check_limit(user_id):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if user_id not in usage or usage[user_id]["date"] != today:
        usage[user_id] = {"count": 0, "date": today}
    if usage[user_id]["count"] >= DAILY_LIMIT:
        return False
    usage[user_id]["count"] += 1
    return True

# ---- Routes ----
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Cerebras Flask API with daily limit running"})

@app.route("/generate", methods=["POST", "OPTIONS"])
def generate():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    # Use IP as user_id (simple) or API key if you have authentication
    user_id = request.remote_addr

    if not check_limit(user_id):
        # Friendly response when limit is reached
        return jsonify({
            "response": f"You’ve reached your daily limit of {DAILY_LIMIT} prompts. Please try again tomorrow."
        }), 429

    data = request.json or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b",
            max_completion_tokens=1024,
            temperature=0.2,
            top_p=1,
            stream=False
        )
        generated_text = completion.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"response": generated_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
