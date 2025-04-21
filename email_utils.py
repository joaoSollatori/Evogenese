import os
from flask_mail import Mail, Message
from dotenv import load_dotenv

# =====================================================
# 1. CONFIGURAÇÃO INICIAL
# =====================================================

load_dotenv()
mail = Mail()


def configurar_mail(app):
    """
    Configura o servidor SMTP para envio de e-mails via SendGrid.
    """
    app.config.update(
        MAIL_SERVER='smtp.sendgrid.net',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME='apikey',
        MAIL_PASSWORD=os.getenv('SENDGRID_API_KEY'),
        MAIL_DEFAULT_SENDER='evogenesesuporte@gmail.com',
        MAIL_MAX_EMAILS=3,
        MAIL_SUPPRESS_SEND=False,
        MAIL_ASCII_ATTACHMENTS=False,
        MAIL_TIMEOUT=15  # Timeout SMTP em segundos
    )
    mail.init_app(app)


# =====================================================
# 2. E-MAIL: REDEFINIÇÃO DE SENHA
# =====================================================

def enviar_email_redefinicao(destinatario, link_redefinicao):
    """
    Envia e-mail com link para redefinição de senha.
    """
    corpo_html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Recuperação de Senha - Evogenêse</title></head>
    <body style="background-color: #0f0f0f; font-family: 'Segoe UI', sans-serif; color: #f2f2f2; padding: 40px 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #1c1c1c; padding: 30px; border-radius: 12px; box-shadow: 0 0 20px rgba(255,69,0,0.2);">
            <h2 style="color: #ff6600; text-align: center;">Você solicitou a recuperação de senha</h2>
            <p style="text-align: center;">Clique no botão abaixo para redefinir sua senha:</p>
            <div style="text-align: center; margin: 24px 0;">
                <a href="{link_redefinicao}" style="padding: 14px 28px; background-color: #ff6600; color: white; text-decoration: none; border-radius: 10px;">
                    Redefinir Senha
                </a>
            </div>
            <p style="text-align: center; font-size: 14px; color: #999999;">Se você não solicitou, ignore este e-mail.</p>
            <div style="text-align: center; margin-top: 40px;">
                <p style="font-size: 15px; color: #bbbbbb;">Com sabedoria e estratégia,</p>
                <p style="font-weight: bold; color: #ff6600;">Evogenêse</p>
            </div>
        </div>
    </body>
    </html>
    """
    return _enviar_email(destinatario, 'Redefinição de Senha - Evogenêse', corpo_html)


# =====================================================
# 3. E-MAIL: CÓDIGO DE VERIFICAÇÃO
# =====================================================

def enviar_email_codigo_verificacao(destinatario, codigo):
    """
    Envia e-mail com código de verificação de identidade.
    """
    corpo_html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Código de Verificação - Evogenêse</title></head>
    <body style="background-color: #0f0f0f; font-family: 'Segoe UI', sans-serif; color: #f2f2f2; padding: 40px 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #1c1c1c; padding: 30px; border-radius: 12px; box-shadow: 0 0 20px rgba(255,69,0,0.2);">
            <h2 style="color: #ff6600; text-align: center;">Seu código de verificação</h2>
            <p style="text-align: center; font-size: 24px; font-weight: bold; color: #ffffff;">{codigo}</p>
            <p style="text-align: center; font-size: 14px; color: #bbbbbb;">Expira em 10 minutos.</p>
            <div style="text-align: center; margin-top: 40px;">
                <p style="font-size: 15px; color: #bbbbbb;">Com sabedoria e estratégia,</p>
                <p style="font-weight: bold; color: #ff6600;">Evogenêse</p>
            </div>
        </div>
    </body>
    </html>
    """
    return _enviar_email(destinatario, 'Código de Verificação - Evogenêse', corpo_html)


# =====================================================
# 4. FUNÇÃO INTERNA DE ENVIO
# =====================================================

def _enviar_email(destinatario, assunto, corpo_html):
    """
    Envia um e-mail HTML usando Flask-Mail com tratamento de erro.
    """
    try:
        msg = Message(subject=assunto, recipients=[destinatario])
        msg.html = corpo_html
        mail.send(msg)
        print(f"[OK] E-mail enviado para {destinatario}: {assunto}")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail para {destinatario} ({assunto}): {e}")
        return False