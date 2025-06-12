from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)
FILE_MAGAZZINO = "magazzino.json"

def carica_magazzino():
    if os.path.exists(FILE_MAGAZZINO):
        with open(FILE_MAGAZZINO, "r") as f:
            return json.load(f)
    return {}

def salva_magazzino(magazzino):
    with open(FILE_MAGAZZINO, "w") as f:
        json.dump(magazzino, f, indent=4)

@app.route("/")
def index():
    magazzino = carica_magazzino()
    return render_template("index.html", magazzino=magazzino)

@app.route("/aggiungi", methods=["POST"])
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

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Prende la porta da Render o usa 5000 di default
    app.run(host="0.0.0.0", port=port, debug=True)

