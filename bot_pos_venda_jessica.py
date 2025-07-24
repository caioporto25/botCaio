
# Requisitos: instale as bibliotecas abaixo se ainda nao tiver instalado
# pip install flask openai pandas

from flask import Flask, request, jsonify
import openai
import pandas as pd
import datetime

# CONFIGURAÇÕES --------------------
import os
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')
CSV_PATH = 'registro_pacientes.csv'
SUPERVISAO_TELEFONE = '21969294282'
SITE_RESULTADOS = 'http://nav.dasa.com.br/'

# Cria ou atualiza a planilha CSV
try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    df = pd.DataFrame(columns=['nome', 'comentario', 'status', 'data'])
    df.to_csv(CSV_PATH, index=False)

# Cria app Flask
app = Flask(__name__)

# Função para construir a mensagem do bot com personalidade premium
def gerar_resposta(user_input, nome_paciente="Paciente"):
    mensagem_inicial = f"Olá, {nome_paciente}! Aqui é a Laura, do atendimento pós-venda da DASA. Esperamos que sua experiência tenha sido excelente! Você já teve acesso aos seus resultados? Caso não, você pode visualizá-los pelo site: {SITE_RESULTADOS}"

    if "hematoma" in user_input.lower():
        return (
            mensagem_inicial +
            "\n\nPercebemos que você relatou hematomas após a coleta. Isso pode ser comum em alguns casos. Algumas dicas úteis:\n"
            "- Aplique compressa fria nas primeiras 24 horas\n"
            "- Evite carregar peso com o braço da coleta\n"
            "- Mantenha o local limpo\n"
            "- Caso persista, procure assistência médica."
        )

    elif any(p in user_input.lower() for p in ['ruim', 'péssimo', 'horrível', 'demorado']):
        print(f"[ALERTA]: Encaminhar para supervisão. Telefone: {SUPERVISAO_TELEFONE}")
        return (
            mensagem_inicial +
            "\n\nSentimos muito pela sua experiência negativa. Sua mensagem foi encaminhada à nossa supervisão e entraremos em contato em breve. Obrigado pelo feedback! 💙"
        )

    elif any(p in user_input.lower() for p in ['bom', 'ótimo', 'excelente', 'adorei']):
        return (
            mensagem_inicial +
            "\n\nFicamos muito felizes com seu retorno positivo! Enviamos uma pesquisa de satisfação para o seu e-mail. Sua opinião é muito importante para nós! 💙"
        )

    else:
        return mensagem_inicial + "\n\nGostaríamos de saber: como foi o seu atendimento conosco?"


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    nome = data.get('nome', 'Paciente')
    mensagem = data.get('mensagem', '')

    resposta = gerar_resposta(mensagem, nome)

    novo_registro = {
        'nome': nome,
        'comentario': mensagem,
        'status': 'processado',
        'data': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    df.loc[len(df)] = novo_registro
    df.to_csv(CSV_PATH, index=False)

    return jsonify({'resposta': resposta})


if __name__ == '__main__':
    app.run(debug=True)
