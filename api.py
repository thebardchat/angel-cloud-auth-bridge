from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ANGEL_CLOUD_API_KEY = os.getenv("ANGEL_CLOUD_API_KEY")
ANGEL_CLOUD_BASE_URL = os.getenv("ANGEL_CLOUD_BASE_URL", "https://api.angel-cloud.dev")

@app.route('/auth/token', methods=['POST'])
def get_angel_cloud_token():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    headers = {
        "X-API-Key": ANGEL_CLOUD_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(f"{ANGEL_CLOUD_BASE_URL}/auth/token", headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Angel Cloud API error: {e.response.text}"}), e.response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network or request error: {e}"}), 500

@app.route('/auth/validate', methods=['POST'])
def validate_angel_cloud_token():
    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({"error": "Token is required"}), 400

    headers = {
        "X-API-Key": ANGEL_CLOUD_API_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{ANGEL_CLOUD_BASE_URL}/auth/validate", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Angel Cloud API error: {e.response.text}"}), e.response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network or request error: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3005)
