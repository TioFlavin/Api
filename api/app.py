from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests

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

# Função para buscar todas as séries sem paginação
def fetch_all_series():
    all_series = []
    page_number = 1
    while True:
        page_series = fetch_series_from_page(page_number)
        if not page_series:
            break
        all_series.extend(page_series)  # Adiciona as séries dessa página à lista total
        page_number += 1
        
    # Retorna todas as séries encontradas
    return all_series

# Rota para buscar todas as séries sem paginação
@app.route("/series/", methods=["GET"])
def get_series():
    all_series = fetch_all_series()  # Busca todas as séries

    # Retornar todas as séries no formato JSON
    return jsonify({
        "total_series": len(all_series),
        "series": all_series
    })

if __name__ == "__main__":
    app.run(debug=True)
