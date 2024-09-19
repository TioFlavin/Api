from flask import Flask, request, jsonify
from googleapiclient.discovery import build

app = Flask(__name__)

YOUTUBE_API_KEY = 'AIzaSyDROWO5FOF3p7JY4Ux58oI8sPsXJfX6jBI'

def youtube_search(query):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    request = youtube.search().list(
        part="snippet",
        maxResults=50,
        q=query
    )
    response = request.execute()
    return response

@app.route('/pesquisa', methods=['GET'])
def pesquisa_youtube():
    query = request.args.get('pesquisa')
    
    if not query:
        return jsonify({"error": "Parâmetro 'pesquisa' é obrigatório"}), 400
    
    # Faz a pesquisa no YouTube
    results = youtube_search(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
