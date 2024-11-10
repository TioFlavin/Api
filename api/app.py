from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Função para buscar informações das séries
def fetch_series_info(page_number):
    url = f"https://doramasonline.org/br/series/pagina/{page_number}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    series_data = []
    
    # Encontrar as séries na página
    series_list = soup.find_all("div", class_="box-serie")
    
    for series in series_list:
        title_tag = series.find("a")
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            image_tag = series.find("img")
            image_url = image_tag["src"] if image_tag else None
            year_tag = series.find("span", class_="year")
            year = year_tag.get_text(strip=True) if year_tag else "Ano não disponível"
            
            series_info = {
                "title": title,
                "link": link,
                "image_url": image_url,
                "year": year
            }
            series_data.append(series_info)
    
    return series_data

# Função para buscar informações de episódios da série
def fetch_episode_info(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    episodes_data = []
    
    # Encontrar a seção de episódios
    episodes_section = soup.find("div", id="episodes")
    if episodes_section:
        # Encontrar todas as temporadas dentro da seção
        seasons = episodes_section.find_all("div", class_="se-c")
        
        for season in seasons:
            season_title_tag = season.find("span", class_="title")
            if season_title_tag:
                season_title = season_title_tag.get_text(strip=True)
            
            episodes = season.find_all("li")
            for episode in episodes:
                episode_number = episode.find("div", class_="numerando")
                episode_title_tag = episode.find("a")
                episode_image_tag = episode.find("img")
                episode_date_tag = episode.find("span", class_="date")
                
                episode_info = {
                    "episode_number": episode_number.get_text(strip=True) if episode_number else "Número não encontrado",
                    "episode_title": episode_title_tag.get_text(strip=True) if episode_title_tag else "Título não encontrado",
                    "episode_link": episode_title_tag["href"] if episode_title_tag else "Link não encontrado",
                    "episode_image": episode_image_tag["src"] if episode_image_tag else "Imagem não encontrada",
                    "episode_year": episode_date_tag.get_text(strip=True) if episode_date_tag else "Ano não encontrado",
                    "season_title": season_title
                }
                episodes_data.append(episode_info)
    
    return episodes_data

# Rota para obter todas as séries com paginação de 1 a 25
@app.route("/series/", methods=["GET"])
def get_series():
    page_number = request.args.get('page', 1, type=int)
    
    if page_number < 1 or page_number > 25:
        return jsonify({"error": "Página inválida. Escolha uma página de 1 a 25."}), 400
    
    series = fetch_series_info(page_number)
    
    if not series:
        return jsonify({"error": "Erro ao buscar as séries."}), 500
    
    return jsonify({
        "series": series
    })

# Rota para obter informações dos episódios de uma série
@app.route("/infor", methods=["GET"])
def get_episode_info():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL não fornecida"}), 400
    
    episodes_info = fetch_episode_info(url)
    
    if not episodes_info:
        return jsonify({"error": "Não foi possível extrair informações dos episódios"}), 404
    
    return jsonify({
        "series_info": episodes_info
    })

if __name__ == "__main__":
    app.run(debug=True)
