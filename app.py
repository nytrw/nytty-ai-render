from flask import Flask, request, jsonify
from flask_cors import CORS
from llama_cpp import Llama

app = Flask(__name__)
CORS(app)

# ---- Load the GGUF model ----
llm = Llama.from_pretrained(
    repo_id="jfer1015/Mistral-7B-Instruct-v0.3-Q4_K_M-GGUF",
    filename="mistral-7b-instruct-v0.3-q4_k_m.gguf"
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Mistral 7B Instruct Flask API running"})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # ---- Generate text ----
    output = llm(prompt, max_tokens=200, temperature=0.7)
    generated_text = output.get("choices")[0]["text"]

    return jsonify({"response": generated_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
