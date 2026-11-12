CREATE TABLE IF NOT EXISTS concerts (
    id INTEGER PRIMARY KEY,
    concert_date TEXT NOT NULL,
    institution TEXT,
    title TEXT NOT NULL,
    price REAL,
    typology TEXT,
    subtypology TEXT,
    program TEXT,
    comment TEXT
);
