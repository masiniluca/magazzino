from flask import Flask, render_template, request, redirect, session, url_for, render_template_string
import json
import os

app = Flask(__name__)
app.secret_key = 'una_chiave_super_segreta'  # Cambiala con una tua chiave sicura

FILE_MAGAZZINO = "magazzino.json"

# Credenziali login semplici
PASSWORD = 'easyservice'

def carica_magazzino():
    if os.path.exists(FILE_MAGAZZINO):
        with open(FILE_MAGAZZINO, "r") as f:
            return json.load(f)
    return {}

def salva_magazzino(magazzino):
    with open(FILE_MAGAZZINO, "w") as f:
        json.dump(magazzino, f, indent=4)

# Pagina login (usiamo template inline per semplicità)
login_page = '''
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post">
  <input name="username" placeholder="Username" required>
  <input name="password" type="password" placeholder="Password" required>
  <input type="submit" value="Login">
</form>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(login_page + "<p style='color:red'>Credenziali errate</p>")
    return render_template_string(login_page)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Decoratore per controllare il login sulle pagine protette
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route("/scansione", methods=["POST"])
@login_required
def scansione():
    codice_raw = request.form["codice"]
    quantità = int(request.form["quantità"])

    tipo = None
    if codice_raw.startswith("A_"):
        tipo = "acquisto"
        codice = codice_raw[2:]
    elif codice_raw.startswith("V_"):
        tipo = "vendita"
        codice = codice_raw[2:]
    else:
        return redirect("/")

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
