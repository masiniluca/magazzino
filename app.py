from flask import Flask, render_template, request, redirect, session, url_for, render_template_string
import json
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'una_chiave_super_segreta'  # Cambiala con una tua chiave sicura

FILE_MAGAZZINO = "magazzino.json"
FILE_LOG = "log.txt"
PASSWORD = 'easyservice'  # Password di accesso

# ------------------- Funzioni di utilità -------------------

def carica_magazzino():
    if os.path.exists(FILE_MAGAZZINO):
        with open(FILE_MAGAZZINO, "r") as f:
            return json.load(f)
    return {}

def salva_magazzino(magazzino):
    with open(FILE_MAGAZZINO, "w") as f:
        json.dump(magazzino, f, indent=4)

def scrivi_log(codice, operazione, quantità):
    with open(FILE_LOG, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {operazione.upper()}: {codice} - Quantità: {quantità}\n")

# ------------------- Autenticazione -------------------

login_page = '''
<!doctype html>
<html>
<head><title>Login</title></head>
<body style="display:flex; justify-content:center; align-items:center; height:100vh; background:#f5f5f5;">
    <form method="post" style="background:white; padding:2rem; border-radius:1rem; box-shadow:0 0 10px rgba(0,0,0,0.1);">
        <h2 style="text-align:center;">🔐 Accesso</h2>
        <input name="password" type="password" placeholder="Password" class="form-control mb-3" required style="width:100%; padding:0.5rem;">
        <button type="submit" class="btn btn-primary" style="width:100%;">Accedi</button>
        {{ errore }}
    </form>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    errore = ""
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            errore = "<p style='color:red; text-align:center;'>Credenziali errate</p>"
    return render_template_string(login_page, errore=errore)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ------------------- Rotte principali -------------------

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
        scrivi_log(codice, "aggiunta", quantità)
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
        scrivi_log(codice, tipo, quantità)
    return redirect("/")

@app.route("/scansione", methods=["POST"])
@login_required
def scansione():
    codice = request.form["codice"]
    quantità = int(request.form["quantità"])
    tipo = request.form["tipo"]

    magazzino = carica_magazzino()
    if codice in magazzino:
        if tipo == "acquisto":
            magazzino[codice]["quantità"] += quantità
        elif tipo == "vendita":
            magazzino[codice]["quantità"] = max(0, magazzino[codice]["quantità"] - quantità)
        salva_magazzino(magazzino)
    return redirect("/")


# ------------------- Avvio -------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
