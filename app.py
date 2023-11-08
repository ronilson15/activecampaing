from flask import Flask, request, jsonify
import requests
import re
from difflib import get_close_matches
from flask_cors import CORS
from urllib.parse import unquote
app = Flask(__name__)
CORS(app)
API_URL = 'https://killerdroom.api-us1.com/api/3'
API_TOKEN = 'f7f87d2ae8ef6f2fe57bb87fc81ee095c317261659713181118562cade7ef514a14e0df6'
LIST_ID = 5
HEADERS = {'Api-Token': API_TOKEN}
MENSAGEM_DE_RESPOSTA = "📋 Agora preciso que você realize seu cadastro em nosso site \n \n 💼 Empresa: Supermercados Atacadão \n \n 🔰 Status: *Aguardando Cadastro.* \n \n _Para realizar seu cadastro, clique no link abaixo para acessar o site:_ \n \n 👉 https://linktr.ee/Realizar.Cadastro \n 👉 https://linktr.ee/Realizar.Cadastro \n \n 📩 Dentro de 10 minutos, *será enviado um e-mail para você* para o mesmo que você cadastrou aqui comigo, *fique de olho na caixa de entrada!* \n \n _Após acessar o site digite *OK* para prosseguir._"
MENSAGEM_DE_ERRO_EMAIL = "❌ E-mail invalido, verifique e digite novamente"

@app.route('/find-city', methods=['GET'])
def find_city():
    user_ip = unquote(request.args.get('ip'))
    response = requests.get(f"https://api.findip.net/{user_ip}/?token=4372df46468649f6a6cb182074f5fe71")
    city_name = response.json()['city']['names']['en']
    return f'{city_name}'

@app.route('/email', methods=['POST'])
def save_email():
    email, error, status = get_email_from_request(request)
    if error:
        return error, status

    create_contact_response = requests.post(
        f'{API_URL}/contacts',
        headers=HEADERS,
        json={
            'contact': {
                'email': email
            }
        }
    )

    if create_contact_response.status_code != 201:
        return jsonify({
    "replies": [
        {
            "message": MENSAGEM_DE_ERRO_EMAIL
        }
    ]
})

    contact_id = create_contact_response.json()['contact']['id']

    add_to_list_response = requests.post(
        f'{API_URL}/contactLists',
        headers=HEADERS,
        json={
            'contactList': {
                'list': LIST_ID,
                'contact': contact_id,
                'status': 1
            }
        }
    )

    if add_to_list_response.status_code != 201:
        return jsonify({'error': 'Falha ao adicionar email na lista do Active.'}), 500

    return jsonify({
        'message': 'Email adicionado com sucesso.',
        'replies': [
            {
                'message': MENSAGEM_DE_RESPOSTA
            }
        ]
    }), 200

def correct_email(email):
    domains = ['@gmail.com', '@hotmail.com', '@outlook.com', '@yahoo.com']

    domain = re.search("@[\w.]+", email)
    
    if domain:
        domain = domain.group()
        match = get_close_matches(domain, domains, n=1, cutoff=0.8)
        
        if match:
            return email.replace(domain, match[0])
    
    return email

def get_email_from_request(request):
    query = request.json.get('query')
    if not query:
        return None, jsonify({'error': 'A propriedade "query" é obrigatória no JSON enviado.'}), 400
    email = query.get('message')
    if not isinstance(email, str):
        return None, jsonify({'error': 'O campo "message" deve ser uma string.'}), 400
    email = correct_email(email)
    if not email:
        return None, jsonify({'error': 'A propriedade "message" é obrigatória dentro de "query".'}), 400
    return email, None, None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6363, debug=True)
