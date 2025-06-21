"""
This is a simple Python Flask application that provides a RESTful API for generating numerological predictions based on user data.
It uses the following libraries:
- Flask
- Flask-CORS
- Flask-PyMongo
- python-dotenv
- requests (for calling Google Generative AI API)
-Special thanks to the Google Generative AI API for generating predictions and Microsoft Github Copilot for code assistance.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

#MongoDB configuration
app.config["MONGO_URI"] = os.getenv("CONNECTION_STRING")
if not app.config["MONGO_URI"]:
     raise Exception("Connection string is not defined in environment variables.")


mongo = PyMongo(app)
users_collection = mongo.db.users

# Google Generative AI API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def get_numerology_prediction(name, dob):
    prompt = (
        f"Act as a numerologist. The user's name is {name}, and date of birth is {dob}. "
        "Give a generic numerology prediction. Please format the response in a friendly and engaging manner. "
        "Alignments and line spacings for each calculations."
    )
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
    if response.status_code == 200:
        result = response.json()
        # Extract the generated text from the response
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Could not generate prediction."
    else:
        return "Error contacting Gemini API."

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        name = data.get('name')
        dob = data.get('dob')
        email = data.get('email')
        # Parse and format dob
        dob_date = datetime.fromisoformat(dob)
        user = {
            "name": name,
            "dob": dob_date,
            "email": email
        }
        users_collection.insert_one(user)
        prediction = get_numerology_prediction(name, dob_date.strftime("%Y-%m-%d"))
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/', methods=['GET'])
def home():
    return "<H1> Sidepro is an awesome tool. Everyone must try it once. </H1>"

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    app.run(host='127.0.0.1', port=port)