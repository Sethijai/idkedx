from flask import Flask, render_template, jsonify, Response
import requests

app = Flask(__name__)

# Headers for API requests
HEADERS = {
    "Accept": "application/json",
    "origintype": "web",
    "token": "e12e952f94535fbeb82b28321fa812a2d8333e79",
    "usertype": "2",
    "Content-Type": "application/x-www-form-urlencoded"
}

BC_URL = "https://edge.api.brightcove.com/playback/v1/accounts/6415636611001/videos/"
LIVESTREAM_TOKEN_URL = "https://spec.iitschool.com/api/v1/livestreamToken"


@app.route('/play/<class_id>', methods=['GET'])
def play_video(class_id):
    try:
        # Fetch class details
        class_detail_url = f"https://spec.iitschool.com/api/v1/class-detail/{class_id}"
        response = requests.get(class_detail_url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            lesson_url = data.get("data", {}).get("class_detail", {}).get("lessonUrl")
            if not lesson_url:
                return jsonify({"error": "Lesson URL not found"}), 404

            # Fetch Brightcove token
            livestream_token_url = f"{LIVESTREAM_TOKEN_URL}?base=web&module=batch&type=brightcove&vid={class_id}"
            token_response = requests.get(livestream_token_url, headers=HEADERS)

            if token_response.status_code == 200:
                token_data = token_response.json()
                brightcove_token = token_data["data"]["token"]
                brightcove_link = f"{BC_URL}{lesson_url}/master.m3u8?bcov_auth={brightcove_token}"

                # Render the player page with the Brightcove link
                return render_template('player.html', video_url=brightcove_link)
            else:
                return jsonify({"error": "Failed to fetch Brightcove token"}), 500
        else:
            return jsonify({"error": "Failed to fetch class details"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
