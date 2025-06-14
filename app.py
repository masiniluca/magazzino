from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Inizializza il database
def init_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE prodotti
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nome TEXT NOT NULL,
                      codice_barre TEXT UNIQUE NOT NULL,
                      quantita INTEGER NOT NULL,
                      prezzo REAL,
                      descrizione TEXT)''')
        
        # Aggiungi alcuni prodotti di esempio
        prodotti_di_esempio = [
            ('Prodotto A', '123456789012', 10, 9.99, 'Descrizione prodotto A'),
            ('Prodotto B', '987654321098', 5, 19.99, 'Descrizione prodotto B'),
            ('Prodotto C', '456789012345', 20, 4.99, 'Descrizione prodotto C')
        ]
        
        c.executemany('INSERT INTO prodotti (nome, codice_barre, quantita, prezzo, descrizione) VALUES (?, ?, ?, ?, ?)', prodotti_di_esempio)
        conn.commit()
        conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prodotti', methods=['GET'])
def get_prodotti():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM prodotti')
    prodotti = c.fetchall()
    conn.close()
    
    # Converti in lista di dizionari
    result = []
    for p in prodotti:
        result.append({
            'id': p[0],
            'nome': p[1],
            'codice_barre': p[2],
            'quantita': p[3],
        })
    
    return jsonify(result)

@app.route('/api/prodotto/<codice_barre>', methods=['GET'])
def get_prodotto(codice_barre):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM prodotti WHERE codice_barre = ?', (codice_barre,))
    prodotto = c.fetchone()
    conn.close()
    
    if prodotto:
        return jsonify({
            'id': prodotto[0],
            'nome': prodotto[1],
            'codice_barre': prodotto[2],
            'quantita': prodotto[3],
        })
    else:
        return jsonify({'error': 'Prodotto non trovato'}), 404

@app.route('/api/prodotto/aggiungi', methods=['POST'])
def aggiungi_prodotto():
    data = request.json
    codice_barre = data.get('codice_barre')
    quantita = data.get('quantita', 1)
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    try:
        # Verifica se il prodotto esiste già
        c.execute('SELECT quantita FROM prodotti WHERE codice_barre = ?', (codice_barre,))
        risultato = c.fetchone()
        
        if risultato:
            # Aggiorna la quantità
            nuova_quantita = risultato[0] + quantita
            c.execute('UPDATE prodotti SET quantita = ? WHERE codice_barre = ?', (nuova_quantita, codice_barre))
        else:
            # Crea un nuovo prodotto (richiede tutti i campi)
            if not all(k in data for k in ['nome']):
                return jsonify({'error': 'Per nuovi prodotti inserire il nome'}), 400
                
            c.execute('INSERT INTO prodotti (nome, codice_barre, quantita) VALUES (?, ?, ?)',
                      (data['nome'], codice_barre, quantita))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/prodotto/rimuovi', methods=['POST'])
def rimuovi_prodotto():
    data = request.json
    codice_barre = data.get('codice_barre')
    quantita = data.get('quantita', 1)
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    try:
        # Verifica se il prodotto esiste
        c.execute('SELECT quantita FROM prodotti WHERE codice_barre = ?', (codice_barre,))
        risultato = c.fetchone()
        
        if not risultato:
            conn.close()
            return jsonify({'error': 'Prodotto non trovato'}), 404
            
        quantita_attuale = risultato[0]
        
        if quantita_attuale < quantita:
            conn.close()
            return jsonify({'error': 'Quantità insufficiente in magazzino'}), 400
            
        nuova_quantita = quantita_attuale - quantita
        
        if nuova_quantita <= 0:
            # Rimuovi il prodotto se la quantità è 0
            c.execute('DELETE FROM prodotti WHERE codice_barre = ?', (codice_barre,))
        else:
            # Aggiorna la quantità
            c.execute('UPDATE prodotti SET quantita = ? WHERE codice_barre = ?', (nuova_quantita, codice_barre))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/prodotto/elimina/<codice_barre>', methods=['DELETE'])
def elimina_prodotto(codice_barre):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    try:
        c.execute('DELETE FROM prodotti WHERE codice_barre = ?', (codice_barre,))
        conn.commit()
        if c.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Prodotto non trovato'}), 404
            
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)