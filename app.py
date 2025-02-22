from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import db_manager
import secrets
import tempfile
import os

"""
This script sets up a basic Flask web application with a single route.
Imports:
    Flask: The main class for creating a Flask application.
    render_template: Renders an HTML template.
    request: Handles incoming request data.
    redirect: Redirects the user to a different endpoint.
    url_for: Generates URLs for the specified endpoint.
    db_manager: Imports the 'db_manager' module.
    secrets: Imports the 'secrets' module to manage the secret key.
"""

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # Generates a secret key

# configurazione della sessione
app.config['SESSION_TYPE'] = 'filesystem' # Tipo di sessione
app.config['SESSION_PERMANENT_LIFETIME'] = 1800 # 30 minuti

# Create upload folder if it doesn't exist
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Add configuration to Flask app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db_manager.create_database() # Creates the database

@app.route('/')
def home():
    # Se l'utente è già loggato (email o admin), mandalo all'arena
    if ('email' in session and session['email']) or ('admin' in session and session['admin']):
        return redirect(url_for('arena'))
    # Altrimenti, mandalo alla pagina di registrazione
    return redirect(url_for('register'))

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('home')) # Redirects the user to the 'home' route

@app.route('/register')
def register():
    # Pulisci la sessione solo se non c'è già un utente loggato
    if not ('email' in session and session['email']) and not ('admin' in session and session['admin']):
        session['email'] = None
        session['admin'] = None
    return render_template('register.html')


@app.route('/errlogin')
def errlogin():
    messaggio = 'Errore: Username o password errati'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errregister')
def errregister():
    messaggio = 'Errore: Email già in uso'
    return render_template('error.html', messaggio=messaggio)

@app.route('/erradmin')
def erradmin():
    messaggio = 'Errore: Nome o password errati'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errregadmin')
def errregadmin():
    messaggio = 'Errore: Nome già in uso'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errsala')
def errsala():
    messaggio = 'Errore: Accesso alla sala non autorizzato'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errarena')
def errarena():
    messaggio = 'Errore: Accesso all\'arena non autorizzato'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errfilm')
def errfilm():
    messaggio = 'Errore: Accesso ai film non autorizzato'
    return render_template('error.html', messaggio=messaggio)


@app.route('/errprenota')
def errprenota():
    messaggio = 'Errore: errore durante la prenotazione'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errelimina')
def errelimina():
    messaggio = 'Errore: errore durante l\'eliminazione della prenotazione'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errproiezione')
def errproiezione():
    messaggio = 'Errore: Accesso alle proiezioni non autorizzato'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errinserisciproiezione')
def errinserisciproiezione():
    messaggio = 'Errore: problema con l\'inserimento della proiezione'
    return render_template('error.html', messaggio=messaggio)

@app.route('/register', methods=['POST'])
def register_user():
    email = request.form['GMLInoltrato']
    password = request.form['PSWRDInoltrato']
    nominativo = request.form['NMTVInoltrato']
    genere = request.form['GNREInoltrato']

    result = db_manager.inserisciProfilo(email, password, nominativo, genere)

    if not result:
        return redirect(url_for('errregister')) # Redirects the user to the 'errregister' route
    
    messaggio = 'Registrazione completata'
    return render_template('login.html', messaggio=messaggio) # Renders the 'login.html' template

@app.route('/login')
def login():
    messaggio = 'Inserisci le tue credenziali'
    return render_template('login.html', messaggio=messaggio) # Renders the 'login.html' template

@app.route('/login', methods=['POST'])
def login_user():
    email = request.form['GMLInoltrato']
    password = request.form['PSWRDInoltrato']

    result = db_manager.autenticazione(email, password)

    if(result):
        session['email'] = email
        session['admin'] = None
        return redirect(url_for('film'))  # Cambiato da 'arena' a 'film'
    else:
        return redirect(url_for('errlogin')) # Redirects the user to the 'errlogin' route

@app.route('/napafini')
def napafini():
    session['email'] = None
    return render_template('adminLog.html')

@app.route('/adminLogin', methods=['POST'])
def adminLog():
    nome = request.form['nome']
    password = request.form['password']

    admin = db_manager.cercaAmministratore(nome, password)

    if(admin):
        session['admin'] = nome
        return redirect(url_for('film'))  # Cambiato da 'arena' a 'film'
    else:
        return redirect(url_for('erradmin'))

@app.route('/napafiniReg')
def napafiniReg():
    if session['admin']:
        return render_template('adminReg.html')
    else:
        return redirect(url_for('erradmin'))

@app.route('/registerAdmin', methods=['POST'])
def register_admin():
    nome = request.form['nome']
    password = request.form['password']

    result = db_manager.registraAdmin(nome, password)

    if not result:
        return redirect(url_for('errregadmin'))

    return redirect(url_for('arena'))

@app.route('/film')
def film():
    try:
        if not session['email'] and not session['admin']:
            return redirect(url_for('errsala'))
        
        profilo = ''
        if session['admin']:
            profilo = {'nominativo': session['admin'], 'isAdmin': True}
        else:
            profilo = db_manager.cercaProfiloEmail(session['email'])
        
        film = db_manager.listaFilm()

        return render_template('movies.html', profilo=profilo, film=film)
    except Exception as e:
        print(f"Errore in film(): {str(e)}")
        return redirect(url_for('errsala'))

@app.route('/inserisciFilm')
def inserisciFilm():
    try: 
        if not session['admin']:
            return redirect(url_for('errfilm'))
        return render_template('inserimentoFilm.html')
    except Exception as e:
        print(f"Errore in inserisciFilm(): {str(e)}")
        return redirect(url_for('errfilm'))
    
@app.route('/eliminaFilm', methods=['POST'])
def eliminaFilm():
    try: 
        if not session['admin']:
            return redirect(url_for('errfilm'))

        id_film = request.form['id_film']
        film = db_manager.cercaFilmConId(id_film)
        
        if film and film['poster_filename']:
            # Elimina il file del poster se esiste
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], film['poster_filename'])
            if os.path.exists(poster_path):
                os.remove(poster_path)

        result = db_manager.eliminaFilm(id_film)

        if result:
            return redirect(url_for('film'))
        return redirect(url_for('errfilm'))
    except Exception as e: 
        print(f"Errore in eliminaFilm(): {str(e)}")
        return redirect(url_for('errfilm'))

@app.route('/inserisciFilm', methods=['POST'])
def inserisci_film():
    if not session['admin']:
        return redirect(url_for('errfilm'))
    
    titolo = request.form['titolo']
    durata = request.form['durata']
    trama = request.form['trama']
    
    # Handle poster upload
    poster_filename = None
    if 'poster' in request.files:
        poster = request.files['poster']
        if poster.filename != '':
            # Generate unique filename
            ext = os.path.splitext(poster.filename)[1]
            poster_filename = secrets.token_hex(8) + ext
            poster.save(os.path.join(app.config['UPLOAD_FOLDER'], poster_filename))

    result = db_manager.inserisciFilm(titolo, durata, trama, poster_filename)

    if result:
        return redirect(url_for('film'))
    else:
        return redirect(url_for('errfilm'))

@app.route('/arena')
def arena():
    try:
        if not session['email'] and not session['admin']:
            return redirect(url_for('errsala'))
        
        profilo = ''
        if session['admin']:
            profilo = {'nominativo': session['admin'], 'isAdmin': True}
        else:
            profilo = db_manager.cercaProfiloEmail(session['email'])

        with db_manager.DB_connect() as connection:
            cursor = connection.execute('SELECT * FROM sale')
            sale = cursor.fetchall()

        return render_template('arena.html', profilo=profilo, sale=sale)
    except Exception as e:
        print(f"Errore in arena(): {str(e)}")
        return redirect(url_for('errarena'))

@app.route('/proiezioni')
def proiezioni():
    try:
        if not session['email'] and not session['admin']:
            return redirect(url_for('errsala'))
        
        # Pulisci le proiezioni scadute prima di mostrare la lista
        db_manager.pulisci_proiezioni_scadute()
        
        profilo = ''
        if session['admin']:
            profilo = {'nominativo': session['admin'], 'isAdmin': True}
        else:
            profilo = db_manager.cercaProfiloEmail(session['email'])

        proiezioni = db_manager.listaProiezioniConDettagli()
        
        return render_template('proiezioni.html', profilo=profilo, proiezioni=proiezioni)
    except Exception as e:
        print(f"Errore in proiezioni(): {str(e)}")
        return redirect(url_for('errarena'))

@app.route('/sala', methods=['GET'])
def sala():
    try:
        if not session['email'] and not session['admin']:
            return redirect(url_for('errsala'))
        
        profilo = ''
        if session['admin']:
            profilo = {'nominativo': session['admin'], 'isAdmin': True}
        else:
            profilo = db_manager.cercaProfiloEmail(session['email'])

        id_sala = request.args.get('id_sala', type=int)
        id_proiezione = request.args.get('id_proiezione', type=int)
        
        if not id_sala or not id_proiezione:
            return redirect(url_for('errsala'))

        # Verifica che la sala esista
        sala = db_manager.cercaSalaConId(id_sala)
        if not sala:
            return redirect(url_for('errsala'))

        # Verifica che la proiezione esista
        proiezione = db_manager.cercaProiezioneConId(id_proiezione)
        if not proiezione:
            return redirect(url_for('errsala'))

        # Verifica che la proiezione sia effettivamente per questa sala
        if proiezione['id_sala'] != id_sala:
            return redirect(url_for('errsala'))

        # Get sala number for display purposes
        sala = db_manager.cercaSalaConId(id_sala)
        if not sala:
            return redirect(url_for('errsala'))

        posti = db_manager.listaPosti()
        posti = [posto for posto in posti if posto['id_sala'] == id_sala]
        
        prenotazioni = db_manager.listaPrenotazioniPerProiezione(id_proiezione)

        posti_con_prenotazioni = []
        for posto in posti:
            posto_info = dict(posto)
            prenotazione = next(
                (p for p in prenotazioni if p['id_posto'] == posto['id']), 
                None
            )
            posto_info['prenotato'] = bool(prenotazione)
            posto_info['id_profilo'] = prenotazione['id_profilo'] if prenotazione else None
            posti_con_prenotazioni.append(posto_info)

        return render_template('sala.html', 
                            titolo1=f'Sala {sala["numero"]}',  # Use sala number from database
                            subtitolo1='Informazioni sulla nostra app', 
                            subtitolo2='Posti', 
                            profilo=profilo, 
                            posti=posti_con_prenotazioni,
                            id_proiezione=id_proiezione)

    except Exception as e:
        print(f"Errore in sala(): {str(e)}")
        return redirect(url_for('errsala'))

@app.route('/prenota', methods=['POST'])
def prenota():
    try:
        id_profilo = None
        nome_admin = None
        
        id_sala = request.args.get('id_sala', type=int)  # Cambiato da numero_sala a id_sala
        id_proiezione = request.args.get('id_proiezione', type=int)
        
        if 'email' in session and session['email']: 
            profilo = db_manager.cercaProfiloEmail(session['email'])
            if profilo:
                id_profilo = profilo['id']
        elif 'admin' in session and session['admin']:
            nome_admin = session['admin']
        
        if not id_profilo and not nome_admin:
            return redirect(url_for('errsala'))

        id_posto = request.form['id_posto']

        if id_profilo:
            result = db_manager.prenotaPosto(id_profilo, id_posto, None, id_proiezione)
        elif nome_admin:
            result = db_manager.prenotaPosto(None, id_posto, nome_admin, id_proiezione)
        
        if result:
            return redirect(url_for('sala', id_sala=id_sala, id_proiezione=id_proiezione))  # Cambiato da numero_sala a id_sala
        else:
            return redirect(url_for('errprenota'))
    except Exception as e:
        print(f"Errore in prenota(): {str(e)}")
        return redirect(url_for('errprenota'))

@app.route('/eliminaPrenotazione', methods=['POST'])
def eliminaPrenotazione():
    try:
        id_profilo = None
        profilo_admin = None
        
        id_sala = request.args.get('id_sala', type=int)
        id_proiezione = request.args.get('id_proiezione', type=int)

        if session['email']:
            id_profilo = db_manager.cercaProfiloEmail(session['email'])['id']
        elif session['admin']:
            profilo_admin = { 'nome': session['admin'], 'isAdmin': True }
        else:
            return redirect(url_for('errelimina'))
        
        id_posto = request.form['id_posto']

        if profilo_admin and profilo_admin['isAdmin']:
            result = db_manager.eliminaPrenotazione(None, id_posto, id_proiezione, profilo_admin['nome'])
        else:
            result = db_manager.eliminaPrenotazione(id_profilo, id_posto, id_proiezione, None)
        
        if result:
            return redirect(url_for('sala', id_sala=id_sala, id_proiezione=id_proiezione))
        else:
            return redirect(url_for('errelimina'))
    except Exception as e:
        print(f"Errore in eliminaPrenotazione(): {str(e)}")
        return redirect(url_for('errelimina'))

@app.route('/eliminaProiezione', methods=['POST'])
def eliminaProiezione():
    try:
        if not session['admin']:
            return redirect(url_for('errfilm'))

        id_proiezione = request.form['id_proiezione']
        result = db_manager.eliminaProiezione(id_proiezione)

        if result:
            return redirect(url_for('proiezioni'))
        else:
            return redirect(url_for('errfilm'))
    except Exception as e:
        print(f"Errore in eliminaProiezione(): {str(e)}")
        return redirect(url_for('errfilm'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
    
def redirectUrl():
    try:
        if ('email' in session and session['email']) or ('admin' in session and session['admin']):
            return redirect(url_for('arena'))
        return redirect(url_for('register'))
    except Exception as e:
        print(f"Errore in redirectUrl(): {str(e)}")
        return redirect(url_for('errsala'))

@app.route('/inserisciProiezioni')
def inserisciProiezioni():
    try:
        if not session['admin']:
            return redirect(url_for('errproiezione'))
        
        film = db_manager.listaFilm()
        sale = db_manager.listaSale()
        
        return render_template('inserimentoProiezioni.html', film=film, sale=sale)
    except Exception as e:
        print(f"Errore in inserisciProiezioni(): {str(e)}")
        return redirect(url_for('errproiezione'))

@app.route('/inserisciProiezioni', methods=['POST'])
def inserisci_proiezione():
    try:
        if not session['admin']:
            return redirect(url_for('errfilm'))
        
        id_film = request.form['id_film']
        id_sala = request.form['id_sala']
        data = request.form['data']
        ora = request.form['ora']
        
        film = db_manager.cercaFilmConId(id_film)
        if not film:
            return redirect(url_for('errfilm'))
        
        result = db_manager.inserisciProiezione(film['titolo'], id_sala, data, ora)
        
        if result:
            return redirect(url_for('proiezioni'))
        else:
            return redirect(url_for('errinserisciproiezione'))
    except Exception as e:
        print(f"Errore in inserisci_proiezione(): {str(e)}")
        return redirect(url_for('errinserisciproiezione'))

@app.route('/proiezioniSala')
def proiezioniSala():
    try:
        if not session['email'] and not session['admin']:
            return redirect(url_for('errsala'))
        
        numero_sala = request.args.get('numero_sala', type=int)
        if not numero_sala:
            return redirect(url_for('errarena'))
        
        # Verifica che la sala esista basandosi sul numero
        sala = db_manager.cercaSalaConNumero(numero_sala)
        if not sala:
            return redirect(url_for('errarena'))
        
        profilo = ''
        if session['admin']:
            profilo = {'nominativo': session['admin'], 'isAdmin': True}
        else:
            profilo = db_manager.cercaProfiloEmail(session['email'])

        proiezioni = db_manager.listaProiezioniPerSala(numero_sala)
        
        return render_template('proiezioniSala.html', 
                            profilo=profilo, 
                            proiezioni=proiezioni,
                            numero_sala=numero_sala)
    except Exception as e:
        print(f"Errore in proiezioniSala(): {str(e)}")
        return redirect(url_for('errarena'))

@app.route('/proiezioniFilm')
def proiezioniFilm():
    try:
        if not session['email'] and not session['admin']:
            return redirect(url_for('errsala'))
        
        id_film = request.args.get('id_film', type=int)
        if not id_film:
            return redirect(url_for('errfilm'))
        
        # Verifica che il film esista
        film = db_manager.cercaFilmConId(id_film)
        if not film:
            return redirect(url_for('errfilm'))
        
        profilo = ''
        if session['admin']:
            profilo = {'nominativo': session['admin'], 'isAdmin': True}
        else:
            profilo = db_manager.cercaProfiloEmail(session['email'])

        proiezioni = db_manager.listaProiezioniPerFilm(id_film)
        
        return render_template('proiezioniFilm.html', 
                            profilo=profilo, 
                            proiezioni=proiezioni,
                            film=film)
    except Exception as e:
        print(f"Errore in proiezioniFilm(): {str(e)}")
        return redirect(url_for('errfilm'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)
