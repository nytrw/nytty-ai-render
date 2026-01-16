from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from cerebras.cloud.sdk import Cerebras

app = Flask(__name__)
CORS(app)  # enable CORS for frontend

# ---- Cerebras client ----
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY")
if not CEREBRAS_API_KEY:
    raise ValueError("CEREBRAS_API_KEY environment variable not set!")

client = Cerebras(api_key=CEREBRAS_API_KEY)

# ---- Routes ----
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Cerebras Flask API running on Render"})

@app.route("/generate", methods=["POST", "OPTIONS"])
def generate():
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b",       # adjust model if needed
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
    # Render sets the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
