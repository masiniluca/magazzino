document.addEventListener('DOMContentLoaded', function() {
    const barcodeInput = document.getElementById('barcode-input');
    const aggiungiBtn = document.getElementById('aggiungi-btn');
    const rimuoviBtn = document.getElementById('rimuovi-btn');
    const prodottoInfo = document.getElementById('prodotto-info');
    const nuovoProdottoForm = document.getElementById('nuovo-prodotto-form');
    const formNuovoProdotto = document.getElementById('form-nuovo-prodotto');
    const inventarioTable = document.getElementById('inventario-table').querySelector('tbody');
    
    let currentBarcode = '';
    
    // Carica l'inventario all'avvio
    loadInventario();
    
    // Gestione scanner codice a barre
    barcodeInput.addEventListener('change', function() {
        currentBarcode = barcodeInput.value.trim();
        if (currentBarcode) {
            checkProdotto(currentBarcode);
        }
    });
    
    // Pulsante aggiungi
    aggiungiBtn.addEventListener('click', function() {
        if (currentBarcode) {
            aggiungiProdotto(currentBarcode);
        } else {
            alert('Prima scansiona un codice a barre');
        }
    });
    
    // Pulsante rimuovi
    rimuoviBtn.addEventListener('click', function() {
        if (currentBarcode) {
            rimuoviProdotto(currentBarcode);
        } else {
            alert('Prima scansiona un codice a barre');
        }
    });
    
    // Form nuovo prodotto
    formNuovoProdotto.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(formNuovoProdotto);
        const data = Object.fromEntries(formData.entries());
        
        fetch('/api/prodotto/aggiungi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Prodotto aggiunto con successo!');
                formNuovoProdotto.reset();
                nuovoProdottoForm.classList.add('hidden');
                barcodeInput.value = '';
                barcodeInput.focus();
                loadInventario();
            } else {
                alert('Errore: ' + (data.error || 'Errore sconosciuto'));
            }
        })
        .catch(error => {
            alert('Errore di connessione: ' + error.message);
        });
    });
    
    // Funzione per verificare un prodotto
    function checkProdotto(codice) {
        fetch(`/api/prodotto/${codice}`)
            .then(response => {
                if (!response.ok) {
                    // Prodotto non trovato, mostra form per nuovo prodotto
                    prodottoInfo.classList.add('hidden');
                    nuovoProdottoForm.classList.remove('hidden');
                    document.getElementById('nuovo-codice').value = codice;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data && !data.error) {
                    // Mostra info prodotto
                    document.getElementById('prodotto-nome').textContent = data.nome;
                    document.getElementById('prodotto-codice').textContent = data.codice_barre;
                    document.getElementById('prodotto-quantita').textContent = data.quantita;
                    
                    prodottoInfo.classList.remove('hidden');
                    nuovoProdottoForm.classList.add('hidden');
                }
            })
            .catch(error => {
                console.error('Errore:', error);
            });
    }
    
    // Funzione per aggiungere un prodotto
    function aggiungiProdotto(codice) {
        fetch('/api/prodotto/aggiungi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                codice_barre: codice,
                quantita: 1
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                checkProdotto(codice);
                loadInventario();
            } else {
                alert('Errore: ' + (data.error || 'Errore sconosciuto'));
            }
        })
        .catch(error => {
            alert('Errore di connessione: ' + error.message);
        });
    }
    
    // Funzione per rimuovere un prodotto
    function rimuoviProdotto(codice) {
        fetch('/api/prodotto/rimuovi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                codice_barre: codice,
                quantita: 1
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                checkProdotto(codice);
                loadInventario();
            } else {
                alert('Errore: ' + (data.error || 'Errore sconosciuto'));
            }
        })
        .catch(error => {
            alert('Errore di connessione: ' + error.message);
        });
    }
    
    // Funzione per caricare l'inventario
    function loadInventario() {
        fetch('/api/prodotti')
            .then(response => response.json())
            .then(data => {
                inventarioTable.innerHTML = '';
                data.forEach(prodotto => {
                    const row = document.createElement('tr');
                    
                    row.innerHTML = `
                        <td>${prodotto.codice_barre}</td>
                        <td>${prodotto.nome}</td>
                        <td>${prodotto.quantita}</td>
                        <td class="actions">
                            <button onclick="aggiungiDaTabella('${prodotto.codice_barre}')">+1</button>
                            <button onclick="rimuoviDaTabella('${prodotto.codice_barre}')">-1</button>
                        </td>
                    `;
                    
                    inventarioTable.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Errore:', error);
            });
    }
    
    // Esponi funzioni globali per i pulsanti nella tabella
    window.aggiungiDaTabella = function(codice) {
        currentBarcode = codice;
        barcodeInput.value = codice;
        aggiungiProdotto(codice);
    };
    
    window.rimuoviDaTabella = function(codice) {
        currentBarcode = codice;
        barcodeInput.value = codice;
        rimuoviProdotto(codice);
    };
});