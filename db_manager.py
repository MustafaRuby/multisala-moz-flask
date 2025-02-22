# File that contains the database' logic and operations isolated

import sqlite3

DATABASE = 'profiliDB.db' # Database name

def DB_connect():
    """
    Connects to the database and returns a connection object.
    Returns:
        connection: A connection object to the database.
    """
    connection = sqlite3.connect(DATABASE) # Connects to the database
    connection.row_factory = sqlite3.Row # Returns rows as dictionaries
    return connection

def create_database():
    with DB_connect() as connection, open('db.sql', 'r') as file:
        # Prima esegui lo script SQL per creare/aggiornare le tabelle
        connection.executescript(file.read())

        # Controlla se la tabella sale è vuota
        cursor = connection.execute('SELECT COUNT(*) FROM sale')
        count = cursor.fetchone()[0]
        
        # Inserisci le sale solo se la tabella è vuota
        if count == 0:
            for sala in range(1, 9):
                connection.execute('INSERT INTO sale (numero) VALUES (?)', (sala,))
                connection.commit()
                
        # Controlla se la tabella posti è vuota
        cursor = connection.execute('SELECT COUNT(*) FROM posti')
        count = cursor.fetchone()[0]
        
        # Inserisci i posti solo se la tabella è vuota
        if count == 0:
            for sala in range(1, 9):
                for row in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
                    for col in range(1, 9):
                        posto = f"{row}{col}"
                        connection.execute('INSERT INTO posti (id_sala, numero) VALUES (?, ?)', (sala, posto))
            connection.commit()

def inserisciProfilo(email, password, nominativo, genere):
    with DB_connect() as connection:
        profili = cercaProfiloEmail(email)
        if profili:
            return False
        connection.execute('INSERT INTO profili (email, password, nominativo, genere) VALUES (?, ?, ?, ?)', (email, password, nominativo, genere))
        connection.commit()
        return True

def listaProfili():
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM profili')
        return cursor.fetchall()

def cercaProfiloEmail(email):
    with DB_connect() as connection: 
        cursor = connection.execute('SELECT * FROM profili WHERE email = ?', (email,))
        return cursor.fetchone()

def autenticazione(email, password):
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM profili WHERE email = ? AND password = ?', (email, password))
        if(cursor.fetchone()):
            return True
        else:
            return False

def listaPosti():
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM posti')
        return cursor.fetchall()

def prenotaPosto(id_profilo, id_posto, admin, id_proiezione):
    with DB_connect() as connection:
        prenotazioni = connection.execute('''
            SELECT * FROM prenotazioni 
            WHERE id_posto = ? AND id_proiezione = ?
        ''', (id_posto, id_proiezione)).fetchall()
        
        if prenotazioni:
            return False
        elif admin:
            connection.execute('''
                INSERT INTO prenotazioni (id_profilo, id_posto, id_proiezione) 
                VALUES ((SELECT nome FROM amministratori WHERE nome = ?), ?, ?)
            ''', (admin, id_posto, id_proiezione))
        else:
            connection.execute('''
                INSERT INTO prenotazioni (id_profilo, id_posto, id_proiezione) 
                VALUES (?, ?, ?)
            ''', (id_profilo, id_posto, id_proiezione))
        
        connection.commit()
        return True

def listaPrenotazioni():
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM prenotazioni')
        return cursor.fetchall()

def eliminaPrenotazione(id_profilo, id_posto, id_proiezione, nome_admin):
    with DB_connect() as connection:
        if nome_admin:
            # Elimina la prenotazione di un admin
            connection.execute('''
                DELETE FROM prenotazioni 
                WHERE id_posto = ? AND id_proiezione = ?
            ''', (id_posto, id_proiezione))
        else:
            # Elimina la prenotazione di un utente normale
            connection.execute('''
                DELETE FROM prenotazioni 
                WHERE id_profilo = ? AND id_posto = ? AND id_proiezione = ?
            ''', (id_profilo, id_posto, id_proiezione))
        
        connection.commit()
        affected = connection.total_changes
        return affected > 0

def listaFilm():
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM film')
        return cursor.fetchall()

def cercaFilmConTitolo(titolo):
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM film WHERE UPPER(titolo) = ?', ( titolo.upper(), ))
        return cursor.fetchone()
    
def cercaFilmConId(id_film):
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM film WHERE id = ?', (id_film,))
        return cursor.fetchone()

def inserisciFilm(titolo, durata, trama, poster_filename):
    try:
        with DB_connect() as connection:
            if cercaFilmConTitolo(titolo):
                return False
            
            connection.execute(
                'INSERT INTO film (titolo, durata, trama, poster_filename) VALUES (?, ?, ?, ?)',
                (titolo, durata, trama, poster_filename)
            )
            connection.commit()
            return True
    except Exception as e:
        print(f"Errore in inserisciFilm: {str(e)}")
        return False

def eliminaFilm(id_film):
    with DB_connect() as connection:
        film = cercaFilmConId(id_film)
        if not film:
            return False
        
        # Prima elimina eventuali proiezioni e relative prenotazioni
        proiezioni = connection.execute('SELECT id FROM proiezioni WHERE id_film = ?', (id_film,)).fetchall()
        for proiezione in proiezioni:
            # Elimina le prenotazioni associate alla proiezione
            connection.execute('DELETE FROM prenotazioni WHERE id_proiezione = ?', (proiezione['id'],))
            # Elimina la proiezione
            connection.execute('DELETE FROM proiezioni WHERE id = ?', (proiezione['id'],))
            
        # Poi elimina il film
        connection.execute('DELETE FROM film WHERE id = ?', (id_film,))
        connection.commit()
        return True

def inserisciProiezione(nome_film, id_sala, data, ora):
    with DB_connect() as connection:
        film = cercaFilmConTitolo(nome_film)
        id_film = film['id']
        durata = film['durata']
        
        # Converti ora (HH:MM) in minuti per calcoli più semplici
        ore, minuti = map(int, ora.split(':'))
        ora_inizio_minuti = ore * 60 + minuti 
        ora_fine_minuti = ora_inizio_minuti + durata + 60  # Aggiungi 60 minuti di buffer
        ora_inizio_minuti_with_buffer = ora_inizio_minuti - 60  # Sottrai 60 minuti di buffer
        
        # Controlla conflitti
        proiezioni = connection.execute('''
            SELECT p.*, f.durata 
            FROM proiezioni p
            JOIN film f ON p.id_film = f.id
            WHERE p.id_sala = ? AND p.data = ?''', 
            (id_sala, data)).fetchall()
        
        for proiezione in proiezioni:
            p_ore, p_minuti = map(int, proiezione['ora'].split(':'))
            p_inizio = p_ore * 60 + p_minuti
            p_fine = p_inizio + proiezione['durata']
            
            # Verifica se c'è una sovrapposizione includendo il buffer di 1 ora
            if not (ora_fine_minuti <= p_inizio or ora_inizio_minuti_with_buffer >= p_fine):
                return False  # Conflitto trovato
        
        # Se non ci sono conflitti, inserisci la nuova proiezione
        connection.execute('INSERT INTO proiezioni (id_film, id_sala, data, ora) VALUES (?, ?, ?, ?)', (id_film, id_sala, data, ora))
        connection.commit()
        return True
    
def eliminaProiezione(id_proiezione):
    with DB_connect() as connection:
        if not connection.execute('SELECT * FROM proiezioni WHERE id = ?', (id_proiezione,)).fetchone():
            return False
        connection.execute('DELETE FROM proiezioni WHERE id = ?', (id_proiezione, ))
        connection.commit()
        return True
    
def cercaProiezioneConId(id_proiezione):
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM proiezioni WHERE id = ?', (id_proiezione,))
        return cursor.fetchone()

def listaProiezioni():
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM proiezioni')
        return cursor.fetchall()

def listaProiezioniConDettagli():
    with DB_connect() as connection:
        cursor = connection.execute('''
            SELECT p.id, p.id_sala, p.data, p.ora, f.titolo, f.durata, s.numero as numero_sala
            FROM proiezioni p
            JOIN film f ON p.id_film = f.id
            JOIN sale s ON p.id_sala = s.id
            ORDER BY p.data, p.ora
        ''')
        return cursor.fetchall()

def listaPrenotazioniPerProiezione(id_proiezione):
    with DB_connect() as connection:
        cursor = connection.execute('''
            SELECT * FROM prenotazioni 
            WHERE id_proiezione = ?
        ''', (id_proiezione,))
        return cursor.fetchall()

def cercaAmministratore(nome, password):
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM amministratori WHERE nome = ? AND password = ?', (nome, password))
        return cursor.fetchone()

def registraAdmin(nome, password):
    with DB_connect() as connection:
        if(cercaAmministratore(nome, password)):
            return False
        
        connection.execute('INSERT INTO amministratori (nome, password) VALUES (?, ?, ?)', (nome, password))
        connection.commit()
        return True

def cercaSalaConId(id_sala):
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM sale WHERE id = ?', (id_sala,))
        return cursor.fetchone()

def cercaSalaConNumero(numero_sala):
    """Cerca una sala usando il suo numero invece che l'ID."""
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM sale WHERE numero = ?', (numero_sala,))
        return cursor.fetchone()
    
def listaProiezioniPerSala(numero_sala):
    with DB_connect() as connection:
        cursor = connection.execute('''
            SELECT p.id, p.id_sala, p.data, p.ora, f.titolo, f.durata
            FROM proiezioni p
            JOIN film f ON p.id_film = f.id
            JOIN sale s ON p.id_sala = s.id
            WHERE s.numero = ?
            ORDER BY p.data, p.ora
        ''', (numero_sala,))
        return cursor.fetchall()

def listaProiezioniPerFilm(id_film):
    """Recupera tutte le proiezioni di un determinato film."""
    with DB_connect() as connection:
        cursor = connection.execute('''
            SELECT p.id, p.id_sala, p.data, p.ora, f.titolo, f.durata, s.numero as numero_sala
            FROM proiezioni p
            JOIN film f ON p.id_film = f.id
            JOIN sale s ON p.id_sala = s.id
            WHERE f.id = ?
            ORDER BY p.data, p.ora
        ''', (id_film,))
        return cursor.fetchall()

def listaSale():
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM sale ORDER BY numero')
        return cursor.fetchall()

def pulisci_proiezioni_scadute():
    """Elimina le proiezioni scadute e le loro prenotazioni."""
    with DB_connect() as connection:
        # Trova le proiezioni scadute
        query_proiezioni_scadute = '''
            SELECT p.id
            FROM proiezioni p
            JOIN film f ON p.id_film = f.id
            WHERE date(p.data) < date('now')
            OR (
                date(p.data) = date('now')
                AND time(p.ora, '+' || f.durata || ' minutes') < time('now')
            )
        '''
        
        # Ottieni gli ID delle proiezioni scadute
        cursor = connection.execute(query_proiezioni_scadute)
        proiezioni_scadute = [row['id'] for row in cursor.fetchall()]
        
        if proiezioni_scadute:
            # Elimina prima le prenotazioni associate
            placeholders = ','.join('?' * len(proiezioni_scadute))
            connection.execute(
                f'DELETE FROM prenotazioni WHERE id_proiezione IN ({placeholders})',
                proiezioni_scadute
            )
            
            # Poi elimina le proiezioni
            connection.execute(
                f'DELETE FROM proiezioni WHERE id IN ({placeholders})',
                proiezioni_scadute
            )
            
            connection.commit()

