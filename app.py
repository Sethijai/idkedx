from flask import Flask, request, jsonify, Response, send_from_directory
import requests

app = Flask(__name__)

# Constants
ACCOUNT_ID = "6415636611001"
BC_URL = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/"
LIVESTREAM_TOKEN_URL = "https://spec.iitschool.com/api/v1/livestreamToken"
HEADERS = {
    "Accept": "application/json",
    "origintype": "web",
    "token": "e12e952f94535fbeb82b28321fa812a2d8333e79",
    "usertype": "2",
    "Content-Type": "application/x-www-form-urlencoded"
}

@app.route('/<class_id>', methods=['GET'])
def serve_player(class_id):
    # Fetch lesson URL
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
            return jsonify({"proxy_url": f"/stream/{class_id}"})
        else:
            return jsonify({"error": "Failed to fetch Brightcove token"}), 500
    else:
        return jsonify({"error": "Failed to fetch class details"}), 500

@app.route('/stream/<class_id>', methods=['GET'])
def proxy_stream(class_id):
    # Fetch lesson URL
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
            
            # Proxy the video stream
            stream_response = requests.get(brightcove_link, stream=True)
            return Response(
                stream_response.iter_content(chunk_size=1024),
                content_type=stream_response.headers.get('Content-Type')
            )
        else:
            return jsonify({"error": "Failed to fetch Brightcove token"}), 500
    else:
        return jsonify({"error": "Failed to fetch class details"}), 500

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
