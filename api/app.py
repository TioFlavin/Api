from flask import Flask, jsonify
from googleapiclient.discovery import build

app = Flask(__name__)

API_KEY = 'AIzaSyDROWO5FOF3p7JY4Ux58oI8sPsXJfX6jBI'
youtube = build('youtube', 'v3', developerKey=API_KEY)

@app.route('/youtube/shots', methods=['GET'])
def get_youtube_shots():
    request = youtube.search().list(
        part='snippet',
        maxResults=100,
        q='shorts',
        type='video',
        videoDuration='short',
        regionCode='BR'  # Filtra para o Brasil
    )
    response = request.execute()
    
    shots = []
    for item in response.get('items', []):
        video_id = item['id']['videoId']
        shots.append({
            'titulo': item['snippet']['title'],
            'videoId': video_id,
            'link': f'https://www.youtube.com/watch?v={video_id}',  # Link do vídeo
            'thumbnail': item['snippet']['thumbnails']['default']['url']
        })
    
    return jsonify(shots)

if __name__ == '__main__':
    app.run(debug=True)
