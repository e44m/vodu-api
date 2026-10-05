import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

@app.route('/parse', methods=['POST'])
def parse():
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        video_url = None
        video_tag = soup.find("video", id="veoplayer_html15_api") or soup.find("video")
        if video_tag:
            video_url = video_tag.get("src") or (video_tag.find("source").get("src") if video_tag.find("source") else None)

        if not video_url:
            matches = re.findall(r'https?://[^\s"\']+\.mp4[^\s"\']*', res.text)
            if matches:
                video_url = matches[0]

        if video_url:
            if video_url.startswith("//"): video_url = "https:" + video_url
            elif video_url.startswith("/"): video_url = "https://movie.vodu.me" + video_url

        sub_url = None
        if video_tag:
            track = video_tag.find("track", attrs={"kind": re.compile(r"subtitles|captions", re.I)})
            if track: sub_url = track.get("src")

        if not sub_url:
            sub_matches = re.findall(r'https?://[^\s"\']+\.(?:vtt|srt)[^\s"\']*', res.text)
            if sub_matches: sub_url = sub_matches[0]

        if sub_url:
            if sub_url.startswith("//"): sub_url = "https:" + sub_url
            elif sub_url.startswith("/"): sub_url = "https://movie.vodu.me" + sub_url

        return jsonify({
            "success": True,
            "video_url": video_url,
            "subtitle_url": sub_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
