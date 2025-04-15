from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

USERNAME = 'admin'
PASSWORD = 'admin'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    device = db.Column(db.String(100), nullable=True)
    subscription_start = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    subscription_end = db.Column(db.Date, nullable=False)

    def is_active(self):
        return datetime.utcnow().date() <= self.subscription_end

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    clients = Client.query.all()
    return render_template('index.html', clients=clients)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        device = request.form['device']
        start_date = datetime.strptime(request.form['subscription_start'], '%Y-%m-%d')
        duration_days = int(request.form['duration_days'])
        end_date = start_date + timedelta(days=duration_days)

        new_client = Client(name=name, email=email, device=device,
                            subscription_start=start_date, subscription_end=end_date)
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_client.html')

@app.route('/delete/<int:id>')
@login_required
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
