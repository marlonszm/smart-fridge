from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from adm import db, Produtos

app = Flask(__name__)
app.config['SECRET_KEY'] = '@Melo1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.sqlite'
db = SQLAlchemy(app)

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    cpf = db.Column(db.String(100), unique=True, nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    saldo = db.Column(db.Numeric(10, 2), nullable=False, default=500.0)

    def __init__(self, usuario, cpf, idade, senha, saldo=500.0):
        self.usuario = usuario
        self.cpf = cpf
        self.idade = idade
        self.senha = senha
        self.saldo = saldo

class Produtos(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    nome  = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)  
    validade = db.Column(db.Date, nullable=False)

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get('usuario').lower().strip()
        senha = request.form.get("senha").lower().strip()

        if not usuario or not senha:
            flash("Preencha todos os campos!", "error")
        else:
            user = Usuarios.query.filter_by(usuario=usuario).first()
            if user and user.senha == senha:
                return redirect(url_for('lista_produtos',  user_id=user.id))  
            else:
                flash("Credenciais inválidas. Tente novamente.", "error")
    return render_template("user/login_user.html")


@app.route('/registrar', methods=["GET", "POST"])
def criar_usuario():
    if request.method == "POST":
        # Converte para minúsculas e remove espaços extras
        usuario = request.form.get('usuario').lower().strip()
        idade = request.form.get('idade').strip()
        cpf = request.form.get('cpf').strip()
        senha = request.form.get('senha').lower().strip()
        
        if not usuario or not cpf or not idade or not senha:
            flash("Preencha todos os campos!", "error")
        elif int(idade) < 18:
            flash("É proibido menores de 18 anos!", "error")
        else:
            usuario_existente = Usuarios.query.filter_by(cpf=cpf).first()
            if usuario_existente:
                flash("CPF já cadastrado!", "error")
            else:
                novo_usuario = Usuarios(usuario, cpf, int(idade), senha)
                db.session.add(novo_usuario)
                db.session.commit()
                return redirect(url_for('login'))
    
    return render_template("user/register_user.html")


@app.route('/lista_produtos/<int:user_id>', methods=["GET"])
def lista_produtos(user_id):
    produtos_disponiveis = Produtos.query.all()
    return render_template("user/lista_produtos.html", produtos=produtos_disponiveis, user_id=user_id)

@app.route('/comprar_produto/<int:produto_id>/<int:user_id>', methods=["POST"])
def comprar_produto(produto_id, user_id):
    produto = Produtos.query.get(produto_id)
    usuario = Usuarios.query.get(user_id)

    if produto and usuario:
        if produto.quantidade > 0:
            if usuario.saldo >= produto.preco:
                usuario.saldo -= produto.preco
                produto.quantidade -= 1
                if produto.quantidade == 0:
                    db.session.delete(produto)
                db.session.commit()
                flash(f'Compra de {produto.nome} realizada com sucesso! Saldo: R${usuario.saldo}', 'success')
            else:
                flash('Saldo insuficiente!', 'error')
        else:
            flash('Produto indisponível!', 'error')
    else:
        flash('Erro ao processar compra!', 'error')

    return redirect(url_for('lista_produtos', user_id=user_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, host='localhost', debug=True)