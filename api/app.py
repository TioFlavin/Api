import requests
from flask import Flask, jsonify, request
import jwt
import datetime

app = Flask(__name__)

SECRET_KEY = "91597726f"

def generate_token(user_id):
    """Gera um token JWT válido por 30 minutos."""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verifica se o token JWT é válido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/api/login', methods=['POST'])
def login():
    """Simula um login para gerar um token JWT."""
    auth_data = request.json

    if auth_data['username'] == 'admin' and auth_data['password'] == 'senha':
        token = generate_token(user_id=1)
        return jsonify({'token': token}), 200

    return jsonify({"error": "Credenciais inválidas"}), 401

def token_required(f):
    """Decorator para proteger rotas com JWT."""
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'error': 'Token não está presente'}), 401

        try:
            user_id = verify_token(token)
            if user_id is None:
                return jsonify({'error': 'Token inválido ou expirado'}), 401
        except:
            return jsonify({'error': 'Token inválido'}), 401

        return f(*args, **kwargs)
    
    decorator.__name__ = f.__name__  # Preserva o nome da função original
    return decorator

@app.route('/api/serie-info', methods=['GET'])
@token_required
def get_serie_info():
    series_id = request.args.get('id')

    if not series_id:
        return jsonify({"error": "O ID da série é necessário"}), 400

    api_url = f"http://meudorama.eu.org/api/season/by/serie/{series_id}/4F5A9C3D9A86FA54EACEDDD635185/7dbfd419-54ba-43ae-a7d3-a8758e98288c/"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response.json())

@app.route('/api/banner', methods=['GET'])
@token_required
def get_banner():
    api_url = "http://meudorama.eu.org/api/first/4F5A9C3D9A86FA54EACEDDD635185/7dbfd419-54ba-43ae-a7d3-a8758e98288c/"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response.json())

@app.route('/api/listadegeneros', methods=['GET'])
@token_required
def get_generos():
    api_url = "http://meudorama.eu.org/api/genre/all/4F5A9C3D9A86FA54EACEDDD635185/7dbfd419-54ba-43ae-a7d3-a8758e98288c/"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response.json())

@app.route('/api/generos', methods=['GET'])
@token_required
def get_poster_by_genre():
    genre_id = request.args.get('id')
    
    if not genre_id:
        return jsonify({"error": "ID do gênero não fornecido"}), 400

    api_url = f"http://meudorama.eu.org/api/poster/by/filtres/{genre_id}/created/0/4F5A9C3D9A86FA54EACEDDD635185/7dbfd419-54ba-43ae-a7d3-a8758e98288c/"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response.json())

@app.route('/api/filmes', methods=['GET'])
@token_required
def get_filmes_by_page():
    page_number = request.args.get('page')

    if not page_number:
        return jsonify({"error": "Número da página não fornecido"}), 400

    api_url = f"http://meudorama.eu.org/api/movie/by/filtres/0/created/{page_number}/4F5A9C3D9A86FA54EACEDDD635185/7dbfd419-54ba-43ae-a7d3-a8758e98288c/"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response.json())

@app.route('/api/doramas', methods=['GET'])
@token_required
def get_doramas_by_page():
    page_number = request.args.get('page')

    if not page_number:
        return jsonify({"error": "Número da página não fornecido"}), 400

    api_url = f"http://meudorama.eu.org/api/serie/by/filtres/0/created/{page_number}/4F5A9C3D9A86FA54EACEDDD635185/7dbfd419-54ba-43ae-a7d3-a8758e98288c/"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response.json())

@app.route('/api/pesquisa', methods=['GET'])
@token_required
def search_by_name():
    name = request.args.get('nome')

    if not name:
        return jsonify({"error": "Nome não fornecido"}), 400

    api_url = f"http://meudorama.eu.org/api/search/{name}/4F5A9C3D9A86FA54EACEDDD635185/7dbfd419-54ba-43ae-a7d3-a8758e98288c/"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response.json())

# Rota que recebe um número de página e faz uma requisição
@app.route('/api/teste', methods=['GET'])
def get_page():
    # Obtém o número da página da query string (?page=NUMERO)
    page_number = request.args.get('page', default=1, type=int)

    # URL base para a requisição
    base_url = "http://appservidor.erremepe.com:80/ajax/appv/appv2_2_0_10.php"
    
    # Parâmetros da URL
    params = {
        'v': '9.9.95',
        'tipo': 'categoria',
        'nome': 'destaques',
        'pagina': page_number,
        'hwid': 'null'
    }

    # Faz a requisição HTTP para o servidor
    response = requests.get(base_url, params=params)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
    
