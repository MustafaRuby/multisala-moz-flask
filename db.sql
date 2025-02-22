CREATE TABLE IF NOT EXISTS profili(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    nominativo TEXT NOT NULL,
    genere TEXT CHECK (genere IN ('M', 'F')) NOT NULL
);

CREATE TABLE IF NOT EXISTS sale(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS posti(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sala INTEGER NOT NULL,
    numero TEXT NOT NULL,
    FOREIGN KEY (id_sala) REFERENCES sale(id)
);

CREATE TABLE IF NOT EXISTS amministratori(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS film(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titolo TEXT NOT NULL,
    durata INTEGER NOT NULL, -- in minuti
    trama TEXT NOT NULL,
    poster_filename TEXT
);

CREATE TABLE IF NOT EXISTS proiezioni(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_film INTEGER NOT NULL,
    id_sala INTEGER NOT NULL,
    data TEXT NOT NULL,
    ora TEXT NOT NULL,
    FOREIGN KEY (id_film) REFERENCES film(id),
    FOREIGN KEY (id_sala) REFERENCES sale(id)
);

DROP TABLE IF EXISTS prenotazioni;
CREATE TABLE prenotazioni(
    id_profilo INTEGER NOT NULL,
    id_posto INTEGER NOT NULL,
    id_proiezione INTEGER NOT NULL,
    PRIMARY KEY (id_profilo, id_posto, id_proiezione),
    FOREIGN KEY (id_profilo) REFERENCES profili(id),
    FOREIGN KEY (id_posto) REFERENCES posti(id),
    FOREIGN KEY (id_proiezione) REFERENCES proiezioni(id)
);

-- Inserimenti di base
DELETE FROM amministratori;
INSERT INTO amministratori (nome, password) VALUES ('Mostafa', 'passw0rd');
