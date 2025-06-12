from flask import Flask, render_template, request, redirect, session, url_for
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'una_chiave_super_segreta_cambiala_subito'

FILE_MAGAZZINO = "magazzino.json"
PASSWORD = 'easyservice'  # Cambia questa password a piacere

def carica_magazzino():
    if os.path.exists(FILE_MAGAZZINO):
        with open(FILE_MAGAZZINO, "r") as f:
            return json.load(f)
    return {}

def salva_magazzino(magazzino):
    with open(FILE_MAGAZZINO, "w") as f:
        json.dump(magazzino, f, indent=4)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = "Password errata, riprova."
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    magazzino = carica_magazzino()
    return render_template("index.html", magazzino=magazzino)

@app.route("/aggiungi", methods=["POST"])
@login_required
def aggiungi():
    codice = request.form["codice"]
    nome = request.form["nome"]
    quantità = int(request.form["quantità"])

    magazzino = carica_magazzino()
    if codice not in magazzino:
        magazzino[codice] = {"nome": nome, "quantità": quantità}
        salva_magazzino(magazzino)
    return redirect("/")

@app.route("/aggiorna", methods=["POST"])
@login_required
def aggiorna():
    codice = request.form["codice"]
    tipo = request.form["tipo"]
    quantità = int(request.form["quantità"])

    magazzino = carica_magazzino()
    if codice in magazzino:
        if tipo == "acquisto":
            magazzino[codice]["quantità"] += quantità
        elif tipo == "vendita":
            magazzino[codice]["quantità"] = max(0, magazzino[codice]["quantità"] - quantità)
        salva_magazzino(magazzino)
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
