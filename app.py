import requests
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

ACCOUNT_ID = "6415636611001"
BCOV_POLICY = "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"

headers = {
    "Accept": "application/json",
    "origintype": "web",
    "token": "e12e952f94535fbeb82b28321fa812a2d8333e79",
    "usertype": "2",
    "Content-Type": "application/x-www-form-urlencoded"
}

def get_brightcove_token(class_id):
    livestream_token_url = f"https://spec.iitschool.com/api/v1/livestreamToken?base=web&module=batch&type=brightcove&vid={class_id}"
    token_response = requests.get(livestream_token_url, headers=headers)
    print("Token API Response:", token_response.json())  # Debugging
    if token_response.status_code == 200:
        token_data = token_response.json()
        return token_data["data"]["token"]
    else:
        print("Error fetching token:", token_response.text)  # Debugging
        return None

def get_brightcove_url(class_id):
    brightcove_token = get_brightcove_token(class_id)
    if brightcove_token:
        bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/{class_id}/master.m3u8?bcov_auth={brightcove_token}"
        print("Brightcove Video URL:", bc_url)  # Debugging
        return bc_url
    else:
        print("Unable to fetch Brightcove token.")  # Debugging
        return None

@app.route('/')
def index():
    return "Welcome to the Brightcove Video Player API!"

@app.route('/<class_id>')
def play_video(class_id):
    brightcove_url = get_brightcove_url(class_id)
    if brightcove_url:
        return render_template('player.html', video_url=brightcove_url)
    else:
        return jsonify({"error": "Unable to fetch video for this class ID."}), 404

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.ge
