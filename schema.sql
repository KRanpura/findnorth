DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS resumeResult;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    passw TEXT NOT NULL,
    user_role VARCHAR(10),
    age INTEGER NOT NULL,
    sex CHAR NOT NULL
);

CREATE TABLE quest_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pdf_filename TEXT NOT NULL,
    job_listing TEXT NOT NULL,
    match_percentage REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);