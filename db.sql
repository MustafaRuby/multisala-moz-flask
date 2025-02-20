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
    numero INTEGER NOT NULL,
    FOREIGN KEY (id_sala) REFERENCES sale(id)
);

CREATE TABLE IF NOT EXISTS prenotazioni(
    id_profilo INTEGER NOT NULL,
    id_posto INTEGER NOT NULL,
    PRIMARY KEY (id_profilo, id_posto),
    FOREIGN KEY (id_profilo) REFERENCES profili(id),
    FOREIGN KEY (id_posto) REFERENCES posti(id)
);

CREATE TABLE IF NOT EXISTS amministratori(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    password TEXT NOT NULL
);

INSERT INTO amministratori (nome, password) VALUES ('Mostafa', 'passw0rd');