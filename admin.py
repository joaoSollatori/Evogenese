import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.security import generate_password_hash
from forms import CriarUsuarioForm  # Certifique-se de que está importando o form correto
import os
from dotenv import load_dotenv

load_dotenv()

# Definindo o decorador admin_required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_email = os.getenv('ADMIN_EMAIL', '').lower()
        user_email = session.get('user_id', '').lower()
        if user_email != admin_email:
            flash("Acesso restrito ao administrador.", "danger")
            return redirect(url_for('login'))  # Redireciona para o login se não for admin
        return f(*args, **kwargs)
    return decorated_function

# Criando o blueprint para as rotas de admin
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# ========== Painel Admin ==========
@admin_bp.route('/admin/painel')
@admin_required
def painel_admin():
    flash("Bem-vindo ao painel administrativo.", "info")  # Mensagem de boas-vindas
    return render_template('painel.html')

# ========== 2. Criar Usuário ==========
@admin_bp.route('/admin/criar-usuario', methods=['GET', 'POST'])
@admin_required
def criar_usuario():
    form = CriarUsuarioForm()

    if form.validate_on_submit():
        nome = form.nome.data.strip()
        email = form.email.data.strip().lower()
        telefone = form.telefone.data.strip()
        senha = form.senha.data

        senha_hash = generate_password_hash(senha)

        con = sqlite3.connect('protocolos.db')
        cur = con.cursor()
        cur.execute("INSERT INTO usuarios (nome, email, telefone, senha) VALUES (?, ?, ?, ?)",
                    (nome, email, telefone, senha_hash))
        con.commit()
        con.close()

        flash(f'Usuário "{nome}" cadastrado com sucesso!', 'success')  # Mensagem de sucesso personalizada
        return redirect(url_for('admin.criar_usuario'))

    if form.errors:
        for field, messages in form.errors.items():
            for message in messages:
                flash(f"Erro no campo '{field}': {message}", "danger")

    return render_template('admin_criar_usuario.html', form=form)

# ========== 3. Logs ==========
@admin_bp.route('/admin/logs')
@admin_required
def exibir_logs():
    con = sqlite3.connect('protocolos.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = cur.fetchall()
    con.close()
    if not logs:
        flash("Nenhum log encontrado.", "warning")
    return render_template('logs.html', logs=logs)

# ========== 4. Histórico de Cálculos ==========
@admin_bp.route('/admin/historico')
@admin_required
def historico_calculos():
    con = sqlite3.connect('protocolos.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM historico_calculos ORDER BY id DESC")
    historico = cur.fetchall()
    con.close()
    if not historico:
        flash("Nenhum cálculo encontrado.", "warning")
    return render_template('historico_calculos.html', historico=historico)

# ========== 5. Estatísticas ==========
@admin_bp.route('/admin/estatisticas')
@admin_required
def estatisticas():
    con = sqlite3.connect('protocolos.db')
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM historico_calculos")
    total_calculos = cur.fetchone()[0]

    con.close()
    return render_template('estatisticas.html', total_usuarios=total_usuarios, total_calculos=total_calculos)

# ========== 6. Notificações ==========
@admin_bp.route('/admin/notificacoes')
@admin_required
def notificacoes():
    con = sqlite3.connect('protocolos.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM notificacoes ORDER BY id DESC")
    notificacoes = cur.fetchall()
    con.close()
    if not notificacoes:
        flash("Nenhuma notificação encontrada.", "warning")
    return render_template('notificacoes.html', notificacoes=notificacoes)

# ========== 7. Modo Manutenção ==========
@admin_bp.route('/admin/modo-manutencao', methods=['GET', 'POST'])
@admin_required
def modo_manutencao():
    if request.method == 'POST':
        status = request.form.get('status')
        con = sqlite3.connect('protocolos.db')
        cur = con.cursor()
        cur.execute("UPDATE configuracoes SET valor = ? WHERE chave = 'modo_manutencao'", (status,))
        con.commit()
        con.close()
        flash('Modo manutenção atualizado!', 'success')
    return render_template('modo_manutencao.html')

# ========== 8. Configurações Avançadas ==========
@admin_bp.route('/admin/configuracoes', methods=['GET', 'POST'])
@admin_required
def configuracoes():
    admin_email = os.getenv('ADMIN_EMAIL', '').lower()

    if request.method == 'POST':
        chave = request.form.get('chave')
        valor = request.form.get('valor')

        con = sqlite3.connect('protocolos.db')
        cur = con.cursor()

        if chave == 'admin_senha':
            senha_hash = generate_password_hash(valor)
            cur.execute("UPDATE usuarios SET senha = ? WHERE LOWER(email) = ?", (senha_hash, admin_email))
        else:
            cur.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, valor))

        con.commit()
        con.close()
        flash('Configuração salva com sucesso!', 'success')

    con = sqlite3.connect('protocolos.db')
    cur = con.cursor()
    cur.execute("SELECT chave, valor FROM configuracoes ORDER BY chave ASC")
    configuracoes = cur.fetchall()
    con.close()

    return render_template('admin_configuracoes.html', configuracoes=configuracoes)

# ========== 9. Rankings ==========
@admin_bp.route('/admin/rankings')
@admin_required
def rankings():
    con = sqlite3.connect('protocolos.db')
    cur = con.cursor()
    cur.execute("""
        SELECT usuario, COUNT(*) as total
        FROM historico_calculos
        GROUP BY usuario
        ORDER BY total DESC
        LIMIT 10
    """)
    ranking = cur.fetchall()
    con.close()
    if not ranking:
        flash("Nenhum ranking encontrado.", "warning")
    return render_template('rankings.html', ranking=ranking)

# ========== 10. Metas ==========
@admin_bp.route('/admin/metas')
@admin_required
def metas():
    return render_template('metas.html')