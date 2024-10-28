from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def extrair_animes(pagina_id=1, limite_por_pagina=None):
    url = f"https://bakashi.tv/animes/page/{pagina_id}/"
    animes_pagina = []
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Seleciona todos os animes na página
        animes = soup.select("div#archive-content article.item.tvshows")
        
        # Se um limite for definido, aplica-o; caso contrário, extrai todos os animes
        if limite_por_pagina:
            animes = animes[:limite_por_pagina]
        
        for anime in animes:
            titulo = anime.select_one("h3 a").text.strip() if anime.select_one("h3 a") else None
            link = anime.select_one("h3 a")['href'] if anime.select_one("h3 a") else None
            ano = anime.select_one("span").text.strip() if anime.select_one("span") else None
            rating = anime.select_one("div.rating").text.strip() if anime.select_one("div.rating") else None
            imagem = anime.select_one("div.poster img")['src'] if anime.select_one("div.poster img") else None
            
            animes_pagina.append({
                "titulo": titulo,
                "link": link,
                "ano": ano,
                "rating": rating,
                "imagem": imagem
            })
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro ao acessar a página {pagina_id}: {str(e)}"}
    
    return animes_pagina

@app.route('/todos', methods=['GET'])
def rota_todos():
    # Obtém o ID da página a partir dos parâmetros da URL
    pagina_id = request.args.get('id', default=1, type=int)
    # Extrai todos os animes da página especificada
    animes = extrair_animes(pagina_id=pagina_id)
    
    return jsonify({"animes": animes})

if __name__ == '__main__':
    app.run(debug=True)
