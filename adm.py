from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '@Melo1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.sqlite'

db = SQLAlchemy(app)

class Admnistradores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    cpf = db.Column(db.String(100), unique=True, nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    
    def __init__(self, usuario, cpf, idade, senha):
        self.usuario = usuario
        self.idade = idade
        self.cpf = cpf
        self.senha = senha

class Produtos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome  = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)  
    validade = db.Column(db.Date, nullable=False)
    
    def __init__(self, nome, quantidade, tipo, preco, validade):
        self.nome = nome
        self.quantidade = quantidade
        self.tipo = tipo
        self.preco = preco
        self.validade = validade    
        
@app.route('/registrar', methods=["GET", "POST"])
def criar_adm():
    if request.method == "POST":
        usuario = request.form.get('usuario').lower()
        idade = request.form.get('idade')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha').lower()
        
        if not usuario or not cpf or not idade or not senha:
            flash("Preencha todos os campos!", "error")
        elif int(idade) < 18:
            flash("É proibido menores de 18 anos!", "error")
        else:
            novo_adm = Admnistradores(usuario, cpf, int(idade), senha)
            db.session.add(novo_adm)
            db.session.commit()
            return redirect(url_for('login'))
    
    return render_template("adm/register.html")

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get('usuario').lower()
        senha = request.form.get("senha").lower()
        if not usuario or not senha:
            flash("Preencha todos os campos!", "error")
        else:
            user = Admnistradores.query.filter_by(usuario=usuario).first()
            if user and user.senha == senha:
                return redirect(url_for('lista_produtos'))  
            else:
                flash("Credenciais inválidas. Tente novamente.", "error")
    return render_template("adm/login.html")

@app.route('/lista_produtos', methods=["GET"])
def lista_produtos():
    page = request.args.get('page', 1, type=int)
    per_page = 4
    todos_produtos = Produtos.query.paginate(page=page, per_page=per_page)
    return render_template("adm/lista_produtos.html", produtos=todos_produtos)

@app.route('/criar_curso', methods=["GET", "POST"])
def criar_produto():
    if request.method == "POST":
        nome = request.form.get('nome')
        quantidade = request.form.get('quantidade')
        tipo = request.form.get('tipo')
        preco = request.form.get('preco')
        validade = request.form.get('validade')
        
        if not nome or not quantidade or not tipo or not preco or not validade:
            flash("Preencha todos os campos", "error")
        else:
            nova_validade = datetime.strptime(validade, '%Y-%m-%d').date()
            produto = Produtos(nome=nome, quantidade=int(quantidade), tipo=tipo, preco=float(preco), validade=nova_validade)
            db.session.add(produto)
            db.session.commit()
            return redirect(url_for('lista_produtos'))
    return render_template("adm/criar_produto.html")

@app.route('/<int:id>/remover_produto', methods=["GET", "POST"])
def remover_produto(id):
    produto = Produtos.query.get(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('lista_produtos'))

@app.route('/<int:id>/editar_produto', methods=["GET", "POST"])
def editar_produto(id):
    produto = Produtos.query.get(id)
    if request.method == "POST":
        nome = request.form.get("nome")
        quantidade = request.form.get("quantidade")
        tipo = request.form.get("tipo")
        preco = request.form.get("preco")
        validade_str = request.form.get("validade")
        validade = datetime.strptime(validade_str, '%Y-%m-%d').date()
        produto.nome = nome
        produto.quantidade = int(quantidade)
        produto.tipo = tipo
        produto.preco = float(preco) 
        produto.validade = validade
        db.session.commit()
        return redirect(url_for('lista_produtos'))
    return render_template("adm/editar_produto.html", produto=produto)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, host='localhost', debug=True)
