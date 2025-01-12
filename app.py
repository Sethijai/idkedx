import requests
from flask import Flask, render_template, jsonify
import re

app = Flask(__name__, template_folder="templates")

# Brightcove account details
ACCOUNT_ID = "6415636611001"
LIVESTREAM_TOKEN_URL = "https://spec.iitschool.com/api/v1/livestreamToken"
CLASS_DETAIL_URL = "https://spec.iitschool.com/api/v1/class-detail"
BC_URL = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/"
HEADERS = {
    "Accept": "application/json",
    "origintype": "web",
    "token": "e12e952f94535fbeb82b28321fa812a2d8333e79",
    "usertype": "2",
    "Content-Type": "application/x-www-form-urlencoded",
}

@app.route('/')
def index():
    return "Welcome to the Brightcove and YouTube Video Player API!"

@app.route('/<class_id>')
def play_video(class_id):
    # Fetch lesson details
    response = requests.get(f"{CLASS_DETAIL_URL}/{class_id}", headers=HEADERS)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch class details"}), 500

    data = response.json()
    lesson_url = data.get("data", {}).get("class_detail", {}).get("lessonUrl")
    if not lesson_url:
        return jsonify({"error": "Lesson URL not found"}), 404

    # Check if lessonUrl is a Brightcove or YouTube video
    if lesson_url.isdigit():
        # Fetch Brightcove token
        token_response = requests.get(
            f"{LIVESTREAM_TOKEN_URL}?base=web&module=batch&type=brightcove&vid={class_id}",
            headers=HEADERS,
        )
        if token_response.status_code != 200:
            return jsonify({"error": "Failed to fetch Brightcove token"}), 500

        token_data = token_response.json()
        brightcove_token = token_data["data"]["token"]

        # Construct Brightcove video URL
        video_url = f"{BC_URL}{lesson_url}/master.m3u8?bcov_auth={brightcove_token}"
        return render_template("player.html", video_url=video_url, is_youtube=False)

    # If lessonUrl is an alphabetic string, treat it as YouTube video
    elif re.match("^[a-zA-Z0-9_-]*$", lesson_url):
        youtube_url = f"https://www.youtube.com/watch?v={lesson_url}"
        return render_template("player.html", video_url=youtube_url, is_youtube=True)

    # If the lessonUrl is invalid
    return jsonify({"error": "Invalid lesson URL format"}), 400

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True)
