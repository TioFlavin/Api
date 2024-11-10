from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
import math

app = Flask(__name__)

# Função para buscar todas as séries de uma página
def fetch_series_from_page(page_number):
    url = f"https://doramasonline.org/br/series/page/{page_number}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    series_list = []
    # Encontrar todos os artigos de série na página
    articles = soup.find_all("article", class_="item tvshows")
    
    for article in articles:
        title_tag = article.find("h3")
        title = title_tag.get_text(strip=True) if title_tag else "Título não encontrado"
        
        link_tag = title_tag.find("a") if title_tag else None
        link = link_tag["href"] if link_tag else None
        
        image_tag = article.find("div", class_="poster").find("img")
        image_url = image_tag["src"] if image_tag else None
        
        year_tag = article.find("span")
        year = year_tag.get_text(strip=True) if year_tag else "Ano não encontrado"
        
        rating_tag = article.find("div", class_="rating")
        rating = rating_tag.get_text(strip=True) if rating_tag else "Avaliação não encontrada"
        
        # Adicionar os dados da série à lista
        series_list.append({
            "title": title,
            "year": year,
            "rating": rating,
            "image_url": image_url,
            "link": link
        })
    
    return series_list

# Função para buscar as séries de todas as páginas até um limite
def fetch_all_series(limit=50):
    all_series = []
    page_number = 1
    while True:
        page_series = fetch_series_from_page(page_number)
        if not page_series:
            break
        all_series.extend(page_series)  # Adiciona as séries dessa página à lista total
        page_number += 1
        
        # Se o número de séries alcançou o limite, interrompe
        if len(all_series) >= limit:
            break
    
    # Retornar as séries limitadas (50 por página)
    return all_series

# Rota para buscar as séries com limite de 50 por página
@app.route("/series/", methods=["GET"])
def get_series():
    page = int(request.args.get('page', 1))  # Pega o número da página (default é 1)
    limit = 50  # Limite de 50 séries por página

    # Buscar todas as séries até o limite
    all_series = fetch_all_series(limit * page)

    # Calcular o número total de páginas
    total_pages = math.ceil(len(all_series) / limit)

    # Calcular o intervalo de séries que será retornado nesta página
    start_index = (page - 1) * limit
    end_index = min(start_index + limit, len(all_series))

    # Pegar as séries para a página atual
    series_for_page = all_series[start_index:end_index]

    # Retornar as séries no formato JSON, com informações sobre a página
    return jsonify({
        "page": page,
        "total_pages": total_pages,
        "total_series": len(all_series),
        "series": series_for_page
    })

if __name__ == "__main__":
    app.run(debug=True)
    
