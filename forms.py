from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

    def validate(self):
        # Chama a validação padrão
        if not super().validate():
            return False
        if self.email.data == "":  # Exemplo de erro personalizado
            self.email.errors.append("O campo de e-mail não pode estar vazio.")
            return False
        return True


class RecuperarSenhaForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar')

    def validate(self):
        # Chama a validação padrão
        if not super().validate():
            return False
        if self.email.data == "":  # Exemplo de erro personalizado
            self.email.errors.append("Digite um e-mail válido.")
            return False
        return True


class ResetarSenhaForm(FlaskForm):
    senha = PasswordField('Nova Senha', validators=[
        DataRequired(),
        Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")
    ])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(),
        EqualTo('senha', message='As senhas precisam ser iguais.')
    ])
    submit = SubmitField('Redefinir Senha')

    def validate(self):
        # Chama a validação padrão
        if not super().validate():
            return False
        if self.senha.data == "":  # Exemplo de erro personalizado
            self.senha.errors.append("A senha não pode estar vazia.")
            return False
        return True


# Novo formulário para criação de usuário
class CriarUsuarioForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    telefone = StringField('Telefone', validators=[DataRequired(), Length(min=10, max=15, message="Telefone inválido")])
    senha = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")
    ])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(),
        EqualTo('senha', message='As senhas precisam ser iguais.')
    ])
    submit = SubmitField('Cadastrar Usuário')

    def validate(self):
        # Chama a validação padrão
        if not super().validate():
            return False
        if self.email.data == "":  # Exemplo de erro personalizado
            self.email.errors.append("E-mail não pode estar vazio.")
            return False
        return True


# Formulário para verificação por código SMS
class ConfirmarSMSForm(FlaskForm):
    codigo = StringField('Código de Verificação', validators=[
        DataRequired(message="Digite o código recebido por SMS."),
        Length(min=6, max=6, message="O código deve ter exatamente 6 dígitos.")
    ])
    submit = SubmitField('Verificar')

    def validate(self):
        # Chama a validação padrão
        if not super().validate():
            return False
        if self.codigo.data == "":  # Exemplo de erro personalizado
            self.codigo.errors.append("O código de verificação não pode estar vazio.")
            return False
        return True