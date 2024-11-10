from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Função para buscar detalhes de uma série a partir de uma URL específica
def fetch_series_data(series_slug):
    url = f"https://doramasonline.org/br/series/{series_slug}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extrair as informações da série
    title_tag = soup.find("h1", class_="title")
    title = title_tag.get_text(strip=True) if title_tag else "Título não encontrado"
    
    year_tag = soup.find("span", class_="year")
    year = year_tag.get_text(strip=True) if year_tag else "Ano não encontrado"
    
    rating_tag = soup.find("span", class_="rating")
    rating = rating_tag.get_text(strip=True) if rating_tag else "Avaliação não encontrada"
    
    image_tag = soup.find("div", class_="poster").find("img")
    image_url = image_tag["src"] if image_tag else None
    
    description_tag = soup.find("div", class_="description")
    description = description_tag.get_text(strip=True) if description_tag else "Descrição não encontrada"
    
    # Retornar os dados da série
    return {
        "title": title,
        "year": year,
        "rating": rating,
        "image_url": image_url,
        "description": description,
        "link": url
    }

# Rota dinâmica para acessar séries usando o "slug" da série na URL
@app.route("/series/<string:series_slug>/")
def get_series_data(series_slug):
    # Buscar os dados da série do site original
    series_data = fetch_series_data(series_slug)
    
    if not series_data:
        return jsonify({"error": "Série não encontrada"}), 404
    
    # Retornar os dados no formato JSON
    return jsonify(series_data)

# Executar o aplicativo Flask
if __name__ == "__main__":
    app.run(debug=True)
