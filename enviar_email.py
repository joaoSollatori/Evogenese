import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

def enviar_email():
    try:
        # Carrega a chave da API do SendGrid
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')

        # Criação do objeto de e-mail
        message = Mail(
            from_email='evogenesesuporte@gmail.com',
            to_emails='joaocarlos.people@gmail.com',
            subject='Teste de E-mail com SendGrid',
            plain_text_content='Este é um e-mail de teste enviado pelo SendGrid.'
        )

        # Envio do e-mail
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)

        print(f'E-mail enviado! Status code: {response.status_code}')
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')

# Chama a função de envio de e-mail
enviar_email()
