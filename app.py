from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import db_manager
import secrets
import tempfile

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

@app.route('/errprenota')
def errprenota():
    messaggio = 'Errore: errore durante la prenotazione'
    return render_template('error.html', messaggio=messaggio)

@app.route('/errelimina')
def errelimina():
    messaggio = 'Errore: errore durante l\'eliminazione della prenotazione'
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
        return redirect(url_for('arena')) # Redirects the user to the 'sala' route
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
        return redirect(url_for('arena'))
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

        posti = db_manager.listaPosti()
        numero_sala = request.args.get('numero_sala', type=int)
        if numero_sala:
            posti = [posto for posto in posti if posto['id_sala'] == numero_sala]
        else:
            return redirect(url_for('errsala'))
            
        prenotazioni = db_manager.listaPrenotazioni()

        # Funzione per aggiungere informazioni sui posti prenotati
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

        return render_template('sala.html', titolo1=f'Sala {numero_sala}', subtitolo1='Informazioni sulla nostra app', subtitolo2='Posti', profilo=profilo, posti=posti_con_prenotazioni)
    except Exception as e:
        print(f"Errore in sala(): {str(e)}")
        return redirect(url_for('errsala'))

@app.route('/prenota', methods=['POST'])
def prenota():
    id_profilo = None
    nome_admin = None
    
    # Ottieni il numero della sala dalla query string
    numero_sala = request.args.get('numero_sala', type=int)
    
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
        result = db_manager.prenotaPosto(id_profilo, id_posto, None)
    elif nome_admin:
        result = db_manager.prenotaPosto(nome_admin, id_posto, True)
    
    if result:
        return redirect(url_for('sala', numero_sala=numero_sala))
    else:
        return redirect(url_for('errprenota'))
        
@app.route('/eliminaPrenotazione', methods=['POST'])
def eliminaPrenotazione():
    id_profilo = None
    profilo_admin = None

    # Ottieni il numero della sala dalla query string
    numero_sala = request.args.get('numero_sala', type=int)

    if session['email']:
        id_profilo = db_manager.cercaProfiloEmail(session['email'])['id']
    elif session['admin']:
        profilo_admin = { 'nome': session['admin'], 'isAdmin': True }
    else:
        return redirect(url_for('errelimina'))
    
    id_posto = request.form['id_posto']

    if profilo_admin and profilo_admin['isAdmin']:
        result = db_manager.eliminaPrenotazione(None, id_posto, profilo_admin['nome'])
        if result:
            return redirect(url_for('sala', numero_sala=numero_sala))
        else:
            return redirect(url_for('errelimina'))
    elif id_profilo:
        result = db_manager.eliminaPrenotazione(id_profilo, id_posto, None)
        if result:
            return redirect(url_for('sala', numero_sala=numero_sala))
        else:
            return redirect(url_for('errelimina'))
    else:
        return redirect(url_for('errsala'))
    
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

if __name__ == '__main__':
    app.run(debug=True, port=3000)
