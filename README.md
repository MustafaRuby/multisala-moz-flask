# 🎬 Cinema Multisala Moz - Sistema di Gestione Completo

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

> Un sistema completo di gestione cinema con catalogo film, proiezioni e prenotazioni, sviluppato con Flask 🚀

## 📝 Descrizione

Sistema integrato per la gestione di un cinema multisala, che include gestione film, proiezioni, sale e prenotazioni. 
Offre un'esperienza personalizzata per utenti e amministratori, con interfacce intuitive e funzionalità complete.

## ✨ Funzionalità Principali

### 👥 Per gli Utenti
- 📝 Registrazione e login semplice
- 🎬 Visualizzazione catalogo film con poster e dettagli
- 🗓️ Consultazione proiezioni per film o per sala
- 🎯 Visualizzazione interattiva dei posti disponibili
- 🎟️ Prenotazione posti per proiezioni specifiche
- ❌ Cancellazione delle proprie prenotazioni

### 👑 Per gli Amministratori
- 🔑 Accesso a pannello amministrativo dedicato
- 🎬 Gestione completa del catalogo film
  - Aggiunta film con poster, durata e trama
  - Rimozione film dal catalogo
- 📅 Gestione proiezioni
  - Programmazione nuove proiezioni
  - Assegnazione film alle sale
  - Gestione orari e date
  - Eliminazione proiezioni
- 🎫 Gestione prenotazioni
  - Visualizzazione stato sale
  - Override prenotazioni utenti
  - Prenotazione/cancellazione posti

## 🏗️ Struttura del Sistema

### Sale e Posti
- 8 sale indipendenti
- 56 posti per sala (7 file A-G × 8 colonne)
- Layout ottimizzato con visualizzazione interattiva
- Sistema di prenotazione real-time

### Gestione Film
- Catalogo film completo
- Upload poster film
- Dettagli film (titolo, durata, trama)
- Visualizzazione proiezioni per film

### Sistema Proiezioni
- Programmazione temporale completa
- Gestione conflitti automatica
- Buffer tra proiezioni
- Pulizia automatica proiezioni scadute

## 🛠️ Tecnologie Utilizzate

- **🐍 Backend**: Python + Flask
- **💾 Database**: SQLite3
- **🎨 Frontend**: HTML5 + CSS3
- **📁 Storage**: Sistema file per poster
- **🔒 Sicurezza**: Flask-Session + Secrets

## 📂 Struttura del Progetto

```
multisala-moz/
│
├── app.py           # Entry point e routing
├── db_manager.py    # Gestione database
├── db.sql          # Schema database
│
├── static/         # File statici
│   └── uploads/    # Poster dei film
│
├── templates/      # Template HTML
│   ├── adminLog.html
│   ├── adminReg.html
│   ├── arena.html
│   ├── error.html
│   ├── inserimentoFilm.html
│   ├── inserimentoProiezioni.html
│   ├── login.html
│   ├── movies.html
│   ├── proiezioni.html
│   ├── proiezioniFilm.html
│   ├── proiezioniSala.html
│   ├── register.html
│   └── sala.html
│
└── README.md
```

## 🚀 Come Iniziare

1. **Clona il repository**
```bash
git clone https://github.com/MustafaRuby/multisala-moz-flask.git
cd multisala-moz-flask
```

2. **Installa le dipendenze**
```bash
pip install flask flask-session
```

3. **Avvia l'applicazione**
```bash
python app.py
```

4. **Accedi all'applicazione**
Apri il browser e vai su `http://localhost:3000`

## 🔐 Sicurezza

- ✅ Gestione sessioni utente
- ✅ Validazione input
- ✅ Protezione route amministrative
- ✅ Upload file sicuro
- ✅ Gestione permessi differenziati

## 🤝 Come Contribuire

1. Fai un fork del progetto
2. Crea un branch per la tua feature
3. Committa i tuoi cambiamenti
4. Pusha sul branch
5. Apri una Pull Request

## 📧 Contatti

Mostafa Abou Elkhir - [abouelkhirmostaffa@email.com](mailto:abouelkhirmostaffa@email.com)

Link Progetto: [https://github.com/MustafaRuby/multisala-moz-flask](https://github.com/MustafaRuby/multisala-moz-flask)

//*Questo progetto è un'evoluzione e una completa migrazione di un progetto che ho fatto precedentemente con javascript (node, express), html, pug e sqlite3. Visita anche quello se sei interessato, ma nota che è molto vecchio rispetto alle modifiche effettuate su questo progetto*: [git clone https://github.com/MustafaRuby/Multisala-cinema.git](git clone https://github.com/MustafaRuby/Multisala-cinema.git)

---
⭐️ Se ti piace questo progetto, metti una stella! ⭐️