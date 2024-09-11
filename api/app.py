from flask import Flask, jsonify, request
import jwt
import datetime

app = Flask(__name__)

# Chave secreta para gerar o token JWT
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Armazenar tokens associados aos IPs
tokens_by_ip = {}

# Função para verificar se o token já existe e se está válido
def get_existing_token(ip_address):
    token_data = tokens_by_ip.get(ip_address)
    if token_data:
        try:
            # Decodifica o token para verificar se ainda é válido
            jwt.decode(token_data['token'], app.config['SECRET_KEY'], algorithms=["HS256"])
            return token_data['token']
        except jwt.ExpiredSignatureError:
            # Token expirado, removemos da lista
            del tokens_by_ip[ip_address]
            return None
        except Exception as e:
            # Qualquer outro erro invalida o token
            del tokens_by_ip[ip_address]
            return None
    return None

# Rota para gerar um novo token que expira em 7 dias, baseado no IP do cliente
@app.route('/api/login', methods=['GET'])
def login():
    # Obtém o IP do cliente
    ip_address = request.remote_addr
    
    # Verifica se já existe um token válido para esse IP
    existing_token = get_existing_token(ip_address)
    if existing_token:
        return jsonify({'message': 'O token já existe para este IP', 'token': existing_token})
    
    # Gera um novo token com expiração de 7 dias
    token = jwt.encode({
        'user': 'admin',
        'ip': ip_address,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    # Armazena o token para o IP
    tokens_by_ip[ip_address] = {'token': token, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}

    return jsonify({'token': token})

# Rota para verificar a data e hora de expiração do token
@app.route('/api/timer', methods=['GET'])
def get_time_left():
    ip_address = request.remote_addr
    
    # Verifica se já existe um token válido para esse IP
    token = get_existing_token(ip_address)
    if not token:
        return jsonify({'message': 'Nenhum token válido para este IP'}), 403

    # Decodifica o token para obter a data de expiração
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        exp_timestamp = data['exp']
        exp_date = datetime.datetime.utcfromtimestamp(exp_timestamp)
        
        # Converte a data no formato solicitado: dd/mm/aaaa horas:minutos:segundos
        exp_date_formatted = exp_date.strftime('%d/%m/%Y horas: %H:%M:%S')
        
        return jsonify({'expires_at': exp_date_formatted})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'O token expirou!'}), 403
    except Exception as e:
        return jsonify({'message': 'Invalid token!'}), 403
        
        
# Rota para verificar e buscar dados da página
@app.route('/api/teste', methods=['GET'])
def get_page():
    # Obtém o ID da página da query string (?page=id_da_pagina)
    page_id = request.args.get('page', default=1, type=int)
    
    # Obtém o token da query string (?token=seu_token)
    token = request.args.get('token')

    if not token or not validate_token(token):
        return jsonify({'error': 'Token is invalid or missing'}), 403

    # URL base da requisição
    base_url = "http://appservidor.erremepe.com:80/ajax/appv/appv2_2_0_10.php"
    
    # Parâmetros da URL
    params = {
        'v': '9.9.95',
        'tipo': 'categoria',
        'nome': 'destaques',
        'pagina': page_id,
        'hwid': 'null'
    }

    # Faz a requisição HTTP para o servidor externo
    response = requests.get(base_url, params=params)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code
        

if __name__ == '__main__':
    app.run(debug=True)
