import joblib
import re
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Define the normalize_amharic function
def normalize_amharic(text):
    if not isinstance(text, str):
        text = str(text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove digits
    text = re.sub(r'\d+', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()

MODEL_CANDIDATES = [
    "amharic_chatbot_improved.pkl",
    "amharic_chatbot_improved.joblib",
    "model.pkl",
    "model.joblib",
    str(Path("models") / "amharic_chatbot_improved.pkl"),
    str(Path("data") / "amharic_chatbot_improved.pkl"),
]

model = None
model_path_used = None

def resolve_model_path():
    mp = os.environ.get("MODEL_PATH")
    if mp:
        return Path(mp)
    for c in MODEL_CANDIDATES:
        p = Path(c)
        if p.exists():
            return p
    return Path(MODEL_CANDIDATES[0])  # default (may not exist)

def load_model():
    global model, model_path_used
    model_path_used = resolve_model_path()
   
    try:
        if not model_path_used.exists():
            print(f"❌ Model file not found at: {model_path_used.resolve()}")
            model = None
            return False
        print(f"📦 Loading model from: {model_path_used.resolve()}")
        model = joblib.load(str(model_path_used))
        print("✅ Model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading model from {model_path_used}: {e}")
        model = None
        return False

# Initial load
load_model()

# Simple demo fallback when model is unavailable
def demo_reply(text: str) -> str:
    t = normalize_amharic(text).lower()
    if any(g in t for g in ["ሰላም", "hello", "hi", "ሀይ"]):
        return "ሰላም! እንኳን ደህና መጣህ/ሽ። እንዴት ልርዳዎት?"
    if any(w in t for w in ["ምን ይሁን", "ምንድን", "help", "እርዳኝ"]):
        return "እባክዎ ጥያቄዎን በግልጽ ቃል ያብራሩ። ምሳሌ፡ ‘የምንጭ ሰዓት ምንድን ነው?’"
    if any(w in t for w in ["አመሰግናለሁ", "እናመሰግናለን", "thanks", "thank you"]):
        return "እኔም እናመሰግናለሁ! ሌላ እንዴት ልርዳ?"
    if len(t) <= 2:
        return "እባክዎ ጥያቄዎን በተስተናጋጅ ሁኔታ ይጻፉ።"
    return f"ይቅርታ፣ ሞዴሉ አልተጫነም። አሁን ለሙከራ ነገር እመልሳለሁ፡ ‘{text}’ ብለዋል።"

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Amharic Chatbot API",
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "demo_mode": os.environ.get("SKIP_MODEL_LOAD") == "1" or model is None,
        "model_path": str(model_path_used.resolve()) if model_path_used else None
    })

@app.route('/chat', methods=['POST'])
def chat():
    if model is None:
        # Demo fallback instead of 503, to keep UI usable
        data = request.get_json(force=True) or {}
        user_question = data.get('question', '')
        if not user_question or not str(user_question).strip():
            return jsonify({'error': 'No question provided'}), 400
        return jsonify({'response': demo_reply(user_question), 'meta': {'mode': 'demo'}}), 200
    
    data = request.get_json(force=True)
    user_question = data.get('question', '')

    if not user_question or not user_question.strip():
        return jsonify({'error': 'No question provided'}), 400

    # Normalize the user's question
    normalized_question = normalize_amharic(user_question)

    # Get the chatbot's response
    try:
        response = model.predict([normalized_question])
        chatbot_response = response[0]
        return jsonify({'response': chatbot_response})
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/admin/reload', methods=['POST', 'GET'])
def reload_model():
    """Reload the model from disk; supports MODEL_PATH env or default candidates."""
    ok = load_model()
    return jsonify({
        "reloaded": ok,
        "model_loaded": model is not None,
        "model_path": str(model_path_used.resolve()) if model_path_used else None,
        "skip": os.environ.get("SKIP_MODEL_LOAD") == "1",
    }), (200 if ok else 500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)