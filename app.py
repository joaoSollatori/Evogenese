# ========== Imports ==========
import os
import random
import sqlite3
import hashlib
import traceback
import string

from datetime import datetime, timedelta
from email_utils import enviar_email_codigo_verificacao, enviar_email_redefinicao
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, EqualTo, Length
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import render_template

# ========== Blueprints ==========
from admin import admin_bp

# ========== Utilitários Próprios ==========
from email_utils import configurar_mail
from forms import RecuperarSenhaForm, ResetarSenhaForm

# ========== Configurações Iniciais ==========
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret')
app.config['WTF_CSRF_TIME_LIMIT'] = None
csrf = CSRFProtect(app)
configurar_mail(app)
serializer = URLSafeTimedSerializer(app.secret_key, salt='senha-reset')
app.register_blueprint(admin_bp)

# ========== Mock para Login ==========
USUARIO = os.getenv('ADMIN_EMAIL', 'admin@evogenetica.com')
SENHA = os.getenv('ADMIN_SENHA', 'supersecreta123')

# ========== Utilitários ==========
def conectar_db():
    return sqlite3.connect('protocolos.db')

def verificar_usuario(email):
    con = conectar_db()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    con.close()
    return usuario

def gerar_codigo_sms():
    return random.randint(100000, 999999)

def generate_reset_token(email):
    return serializer.dumps({'email': email})

# ========== Formulário ==========
class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    senha = PasswordField('Senha', validators=[InputRequired()])
    lembrar = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

# Formulário para confirmação de código
class ConfirmarCodigoForm(FlaskForm):
    codigo = StringField('Digite o código que você recebeu:', validators=[InputRequired()])
    submit = SubmitField('Verificar')

# ========== Rotas ==========

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        print(f"[DEBUG] Sessão ativa! Usuário logado: {session['user_id']}")
        return redirect(url_for('home'))
    else:
        print("[DEBUG] Sessão não ativa. Iniciando processo de login.")

    form = LoginForm()

    if request.method == 'POST' and form.validate():
        email = form.email.data
        senha = form.senha.data
        lembrar = form.lembrar.data

        print(f"[DEBUG] Formulário validado: E-mail: {email} - Lembrar-me: {lembrar}")

        conn = sqlite3.connect('protocolos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        conn.close()

        print(f"[DEBUG] Resultado da consulta ao banco de dados: {resultado}")

        if resultado:
            senha_salva = resultado[0]
            if check_password_hash(senha_salva, senha):
                print("[DEBUG] Senha correta! Redirecionando usuário para o painel.")
                session['user_id'] = email
                destino = url_for('admin.painel_admin') if email == USUARIO else url_for('home')
                resp = make_response(redirect(destino))

                if lembrar:
                    resp.set_cookie('user_email', email, max_age=60*60*24*30)
                    print(f"[DEBUG] Cookie de 'lembrar-me' configurado para o e-mail: {email}")
                elif request.cookies.get('user_email'):
                    resp.delete_cookie('user_email')
                    print("[DEBUG] Cookie 'lembrar-me' deletado.")

                return resp
            else:
                print("[DEBUG] Senha incorreta!")
                flash("xii, vacilou, tem algo errado aí.", "danger")
        else:
            print("[DEBUG] Usuário não encontrado no banco de dados.")
            flash("Usuário não encontrado. Confere aí, jovem!", "danger")

        return render_template('login.html', form=form)

    if 'user_email' in request.cookies:
        form.email.data = request.cookies.get('user_email')
        print(f"[DEBUG] Recuperando e-mail do cookie: {form.email.data}")

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    is_admin = session.get('admin')
    session.pop('user_id', None)
    session.pop('admin', None)
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('user_email')

    if is_admin:
        flash("Você saiu com sucesso!", "success")

    return resp

@app.route('/home')
def home():
    if 'user_id' not in session:
        flash("Você precisa estar logado para acessar o home.", "warning")
        return redirect(url_for('login'))
    return render_template('home.html', usuario=session.get('user_id'))

@app.route('/esqueci-minha-senha', methods=['GET', 'POST'])
def esqueci_minha_senha():
    form = RecuperarSenhaForm()

    if request.method == 'POST' and form.validate():
        email = form.email.data
        usuario = verificar_usuario(email)

        if not usuario:
            flash("Usuário não encontrado, revise a ortografia e tente novamente.", "danger")
            return render_template('esqueci_minha_senha.html', form=form)

        try:
            token = generate_reset_token(email)
            link_recuperacao = url_for('resetar_senha', token=token, _external=True)
            sucesso = enviar_email_redefinicao(email, link_recuperacao)
            mensagem = f'Instruções enviadas para o email {email}!' if sucesso else "Erro ao enviar o e-mail. Tente novamente."
            flash(mensagem, "success" if sucesso else "danger")
            return render_template('esqueci_minha_senha.html', form=form)
        except Exception:
            print("Erro ao enviar e-mail:\n", traceback.format_exc())
            flash("Erro inesperado ao enviar o e-mail. Tente novamente.", "danger")
            return render_template('esqueci_minha_senha.html', form=form)

    return render_template('esqueci_minha_senha.html', form=form)

@app.route('/resetar-senha/<token>', methods=['GET', 'POST'])
def resetar_senha(token):
    form = ResetarSenhaForm()

    try:
        dados = serializer.loads(token, max_age=3600)
        email = dados['email']
    except (SignatureExpired, BadSignature):
        flash("Link expirado ou inválido. Solicite um novo.", "danger")
        return redirect(url_for('esqueci_minha_senha'))

    if request.method == 'POST' and form.validate():
        nova_senha = form.senha.data
        confirmar_senha = form.confirmar_senha.data

        if nova_senha == confirmar_senha:
            senha_hash = generate_password_hash(nova_senha)

            con = conectar_db()
            cursor = con.cursor()
            cursor.execute("UPDATE usuarios SET senha = ? WHERE email = ?", (senha_hash, email))
            con.commit()
            con.close()

            # Geração e envio do código de verificação
            codigo = ''.join(random.choices(string.digits, k=6))
            validade = datetime.now() + timedelta(minutes=10)

            con = conectar_db()
            cursor = con.cursor()
            cursor.execute("UPDATE usuarios SET codigo_verificacao = ?, validade_codigo = ? WHERE email = ?", (codigo, validade, email))
            con.commit()
            con.close()

            # Armazenar o código na session
            session['codigo_verificacao'] = codigo
            session['email_verificacao'] = email

            enviar_email_codigo_verificacao(email, codigo)
            flash("Código de verificação enviado para seu e-mail.", "success")

            return redirect(url_for('confirmar_codigo'))
        else:
            flash("As senhas não coincidem. Tente novamente.", "danger")

    return render_template('resetar_senha.html', form=form, email=email)

@app.route('/confirmar_codigo', methods=['GET', 'POST'])
def confirmar_codigo():
    if 'codigo_verificacao' not in session:
        flash("Sem código? Sem glória! Inicie o processo de recuperação para trilhar o caminho.", "warning")
        return redirect(url_for('esqueci_minha_senha'))

    form = ConfirmarCodigoForm()

    if request.method == 'POST' and form.validate():
        codigo_digitado = form.codigo.data
        codigo_esperado = session.get('codigo_verificacao')

        if codigo_digitado == codigo_esperado:
            flash("Código validado com sucesso! Você provou ser um verdadeiro Evo em meio ao caos.", "success")
            session.pop('codigo_verificacao', None)
            session.pop('email_verificacao', None)
            return redirect(url_for('login'))
        else:
            flash("Código incorreto! Tente de novo ou reinicie sua jornada.", "danger")

    return render_template('confirmacao_codigo.html', form=form)

# ========== Função Única de Status API ==========
@app.route('/admin/status-api')
def status_api():
    status_info = {
        "api_online": True,
        "resposta_ultima_ping": "38ms",
        "uptime": "99.97%",
        "versao": "v1.2.7"
    }
    return render_template('status_api.html', status=status_info)
