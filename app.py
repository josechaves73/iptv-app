from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app = Flask(__name__, template_folder='templates', static_folder='static')app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    clientes = Cliente.query.all()
    return render_template('index.html', clientes=clientes)

@app.route('/add', methods=['GET', 'POST'])
def add_client():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        ip = request.form['ip']
        estado = request.form['estado']
        nuevo_cliente = Cliente(nombre=nombre, ip=ip, estado=estado)
        db.session.add(nuevo_cliente)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_client.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = user.username
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
