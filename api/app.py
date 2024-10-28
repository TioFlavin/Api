from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def extrair_animes(num_paginas=23, limite_por_pagina=5):  # Padrão de 23 páginas, 10 animes por página
    todos_animes = []
    
    for num in range(1, num_paginas + 1):  # Loop de 1 até o número de páginas (1 a 23)
        url = f"https://bakashi.tv/animes/page/{num}/"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Seleciona cada anime individualmente
            animes = soup.select("div#archive-content article.item.tvshows")[:limite_por_pagina]  # Limita a 10 animes por página
            
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
    animes = extrair_animes(num_paginas=23, limite_por_pagina=10)  # Define o limite de páginas e animes por página
    return jsonify({"animes": animes})

if __name__ == '__main__':
    app.run(debug=True)
