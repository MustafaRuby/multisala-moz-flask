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

def prenotaPosto(id_profilo, id_posto, admin):
    with DB_connect() as connection:
        prenotazioni = connection.execute('SELECT * FROM prenotazioni WHERE id_posto = ?', (id_posto,)).fetchall()
        if prenotazioni:
            return False
        elif(admin):
            connection.execute('INSERT INTO prenotazioni (id_profilo, id_posto) VALUES ((SELECT nome FROM amministratori WHERE nome = ?), ?)', (id_profilo, id_posto))
            connection.commit()
            return True
        else:
            connection.execute('INSERT INTO prenotazioni (id_profilo, id_posto) VALUES (?, ?)', (id_profilo, id_posto))
            connection.commit()
            return True

def listaPrenotazioni():
    with DB_connect() as connection:
        cursor = connection.execute('SELECT * FROM prenotazioni')
        return cursor.fetchall()

def eliminaPrenotazione(id_profilo, id_posto, nome_admin):
    with DB_connect() as connection:
        if nome_admin:
            # Elimina la prenotazione direttamente usando solo l'id_posto
            connection.execute('DELETE FROM prenotazioni WHERE id_posto = ?', (id_posto,))
            connection.commit()
            return True
        else:
            # Verifica e elimina la prenotazione per utenti normali
            cursor = connection.execute('SELECT * FROM prenotazioni WHERE id_profilo = ? AND id_posto = ?', (id_profilo, id_posto))
            if not cursor.fetchone():
                return False
            connection.execute('DELETE FROM prenotazioni WHERE id_profilo = ? AND id_posto = ?', (id_profilo, id_posto))
            connection.commit()
            return True

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
