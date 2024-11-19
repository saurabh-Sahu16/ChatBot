from flask import Flask, render_template, request, jsonify
from chat import get_response  # Ensure get_response is defined in chat.py
from deep_translator import GoogleTranslator
from langdetect import detect_langs, detect, LangDetectException

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index_get():
    return render_template("base.html")

@app.route("/predict", methods=["POST"])
def predict():
    text = request.get_json().get("message")
    
    # Check if text is valid
    if not text or text.strip() == "":
        return jsonify({"answer": "Please provide a valid message."}), 400

    try:
        # Bypass language detection for common short English words
        if text.lower() in ["hello", "hi", "hey","bye","goodbye"]:
            lang = "en"
        # elif len(text) <= 3:
        #     lang = "en"  # Assume English for very short texts
        else:
            # Detect language with confidence levels
            lang_probs = detect_langs(text)
            lang = "en" if "en" in [prob.lang for prob in lang_probs[:2]] else lang_probs[0].lang

        print(f"Detected language: {lang}")
        
        # Translate to English if necessary
        if lang != "en":
            text = GoogleTranslator(source=lang, target='en').translate(text)

        # Get response from the chatbot
        response_text = get_response(text)
        
        # Translate the response back to the original language if necessary
        if lang != "en":
            response_text = GoogleTranslator(source='en', target=lang).translate(response_text)

        return jsonify({"answer": response_text})

    except LangDetectException:
        return jsonify({"answer": "Sorry, we couldn't detect the language."}), 400
    except Exception as e:
        return jsonify({"answer": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
