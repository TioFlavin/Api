import requests
from flask import Flask, jsonify, request
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# Chave secreta para gerar o token JWT
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Função para verificar se o token é válido
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')  # Obtém o token da query string

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

# Rota para gerar um novo token que expira em 7 dias
@app.route('/login', methods=['GET'])
def login():
    # Gera um token com expiração de 7 dias
    token = jwt.encode({
        'user': 'admin',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

# Rota para verificar a data e hora de expiração do token
@app.route('/timer', methods=['GET'])
@token_required
def get_time_left():
    token = request.args.get('token')
    
    try:
        # Decodifica o token para obter a data de expiração
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

# Rota que recebe um número de página e faz uma requisição, protegida por token
@app.route('/api/teste', methods=['GET'])
@token_required
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
    
