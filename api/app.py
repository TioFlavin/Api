from flask import Flask, request, jsonify, send_file
import requests
import re
from pytube import YouTube
import os

app = Flask(__name__)

API_KEY = 'AIzaSyDROWO5FOF3p7JY4Ux58oI8sPsXJfX6jBI'

def extract_playlist_id(url):
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

@app.route('/playlist', methods=['GET'])
def get_playlist_videos():
    url = request.args.get('link')
    playlist_id = extract_playlist_id(url)

    if not playlist_id:
        return jsonify({'error': 'Invalid playlist URL'}), 400

    videos = []
    next_page_token = None

    while True:
        api_url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&key={API_KEY}&maxResults=50'
        if next_page_token:
            api_url += f'&pageToken={next_page_token}'

        response = requests.get(api_url)
        data = response.json()

        for item in data.get('items', []):
            title = item['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
            videos.append({'title': title, 'url': video_url})

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    return jsonify(videos)

@app.route('/search', methods=['GET'])
def search_playlists():
    query = request.args.get('pesquisa')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    # Escape special characters for the query string
    query = requests.utils.quote(query)

    api_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=10&type=playlist&q={query}&key={API_KEY}'
    response = requests.get(api_url)
    data = response.json()

    playlists = []
    for item in data.get('items', []):
        title = item['snippet']['title']
        playlist_id = item['id']['playlistId']
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        playlists.append({'title': title, 'url': playlist_url})

    return jsonify(playlists)

@app.route('/download_audio', methods=['GET'])
def download_audio():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'No video URL provided'}), 400

    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(only_audio=True).first()
        file_path = stream.download(filename='audio.mp4')  # Save as audio.mp4 or other format

        return send_file(file_path, as_attachment=True, attachment_filename='audio.mp4')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the downloaded file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True)
    
