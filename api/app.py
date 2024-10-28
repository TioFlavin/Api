from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

def extrair_animes():
    todos_animes = []
    
    for num in range(1, 24):  # De 1 até 23
        url = f"https://bakashi.tv/animes/page/{num}/"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Seleciona cada anime individualmente
            animes = soup.select("div#archive-content article.item.tvshows")
            
            for anime in animes:
                titulo = anime.select_one("h3 a").text.strip() if anime.select_one("h3 a") else None
                link = anime.select_one("h3 a")['href'] if anime.select_one("h3 a") else None
                ano = anime.select_one("span").text.strip() if anime.select_one("span") else None
                rating = anime.select_one("div.rating").text.strip() if anime.select_one("div.rating") else None
                imagem = anime.select_one("div.poster img")['src'] if anime.select_one("div.poster img") else None
                
                todos_animes.append({
                    "titulo": titulo,
                    "link": link,
                    "ano": ano,
                    "rating": rating,
                    "imagem": imagem
                })
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao acessar a página {num}: {str(e)}"}
    
    return todos_animes

@app.route('/todas', methods=['GET'])
def rota_todas():
    animes = extrair_animes()
    return jsonify({"animes": animes})

def extrair_iframes_e_players(url, apenas_principal=False):
    try:
        # Requisição à página alvo
        response = requests.get(url)
        response.raise_for_status()
        
        # Faz o parsing do conteúdo HTML com BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Localiza todos os iframes
        iframes = soup.select("div.dooplay_player div.source-box div.pframe iframe")
        iframe_links = []
        
        for iframe in iframes:
            if 'src' in iframe.attrs:
                src_url = iframe['src']
                # Remove o prefixo e decodifica a URL
                if src_url.startswith("https://bakashi.tv/aviso/?url="):
                    src_url = src_url.replace("https://bakashi.tv/aviso/?url=", "")
                    src_url = urllib.parse.unquote(src_url)
                iframe_links.append(src_url)
        
        # Localiza todos os nomes dos players
        player_options = soup.select("ul#playeroptionsul li.dooplay_player_option")
        players = [
            {
                "name": option.select_one("span.title").text,
                "quality": option.select_one("span.flag img")["src"] if option.select_one("span.flag img") else None
            }
            for option in player_options
        ]

        # Associa os iframes com os players conforme a ordem
        players_with_iframes = []
        for i, (player, iframe_link) in enumerate(zip(players, iframe_links)):
            players_with_iframes.append({
                "order": i + 1,  # Ordem do player
                "name": player["name"],
                "quality": player["quality"],
                "iframe": iframe_link
            })

        # Retorna apenas o primeiro player para a rota principal
        if apenas_principal and players_with_iframes:
            return [players_with_iframes[4]]

        return players_with_iframes

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "Erro ao processar a página"}

@app.route('/principal', methods=['GET'])
def rota_principal():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    resultado = extrair_iframes_e_players(url, apenas_principal=True)
    return jsonify({"players": resultado})

@app.route('/todos', methods=['GET'])
def rota_todos():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    resultado = extrair_iframes_e_players(url, apenas_principal=False)
    return jsonify({"players": resultado})

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
