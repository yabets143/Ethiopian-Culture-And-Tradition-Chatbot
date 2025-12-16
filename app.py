import joblib
import re
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

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

# Load model - handle errors
try:
    model = joblib.load('amharic_chatbot_improved.pkl')
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

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
        "model_loaded": model is not None
    })

@app.route('/chat', methods=['POST'])
def chat():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)