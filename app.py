import requests
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# Constants
ACCOUNT_ID = "6415636611001"
BCOV_POLICY = "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"
BC_URL = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/"
LIVESTREAM_TOKEN_URL = "https://spec.iitschool.com/api/v1/livestreamToken"
CLASS_DETAIL_URL = "https://spec.iitschool.com/api/v1/class-detail/"
HEADERS = {
    "Accept": "application/json",
    "origintype": "web",
    "token": "e12e952f94535fbeb82b28321fa812a2d8333e79",
    "usertype": "2",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Function to fetch Brightcove token
def get_brightcove_token(class_id):
    livestream_token_url = f"{LIVESTREAM_TOKEN_URL}?base=web&module=batch&type=brightcove&vid={class_id}"
    token_response = requests.get(livestream_token_url, headers=HEADERS)
    print("Token API Response:", token_response.json())  # Debugging
    if token_response.status_code == 200:
        token_data = token_response.json()
        return token_data["data"]["token"]
    else:
        print("Error fetching token:", token_response.text)  # Debugging
        return None

# Function to fetch video URL using class_id
def get_brightcove_url(class_id):
    brightcove_token = get_brightcove_token(class_id)
    if brightcove_token:
        bc_url = f"{BC_URL}{class_id}/master.m3u8?bcov_auth={brightcove_token}"
        print("Brightcove Video URL:", bc_url)  # Debugging
        return bc_url
    else:
        print("Unable to fetch Brightcove token.")  # Debugging
        return None

# Function to fetch video URL using lessonUrl
def get_lesson_url(class_id):
    class_detail_url = f"{CLASS_DETAIL_URL}{class_id}"
    response = requests.get(class_detail_url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        lesson_url = data.get("data", {}).get("class_detail", {}).get("lessonUrl")
        if not lesson_url:
            print("Lesson URL not found")  # Debugging
            return None
        brightcove_token = get_brightcove_token(class_id)
        if brightcove_token:
            brightcove_link = f"{BC_URL}{lesson_url}/master.m3u8?bcov_auth={brightcove_token}"
            print("Brightcove Lesson URL:", brightcove_link)  # Debugging
            return brightcove_link
    else:
        print("Error fetching class details:", response.text)  # Debugging
        return None

@app.route('/')
def index():
    return "Welcome to the Brightcove Video Player API!"

@app.route('/<class_id>')
def play_video(class_id):
    # Try fetching using class_id
    brightcove_url = get_brightcove_url(class_id)
    if not brightcove_url:
        # If class_id method fails, try lessonUrl method
        brightcove_url = get_lesson_url(class_id)
    
    if brightcove_url:
        return render_template('player.html', video_url=brightcove_url)
    else:
        return jsonify({"error": "Unable to fetch video for this class ID."}), 404

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
