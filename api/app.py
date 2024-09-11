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
        return jsonify({'message': 'Token already exists for this IP', 'token': existing_token})
    
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
        return jsonify({'message': 'No valid token for this IP'}), 403

    # Decodifica o token para obter a data de expiração
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        exp_timestamp = data['exp']
        exp_date = datetime.datetime.utcfromtimestamp(exp_timestamp)
        
        # Converte a data no formato solicitado: dd/mm/aaaa horas:minutos:segundos
        exp_date_formatted = exp_date.strftime('%d/%m/%Y horas: %H:%M:%S')
        
        return jsonify({'expires_at': exp_date_formatted})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403
    except Exception as e:
        return jsonify({'message': 'Invalid token!'}), 403

if __name__ == '__main__':
    app.run(debug=True)
