CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    passw TEXT NOT NULL,
    user_role VARCHAR(10),
    age INTEGER NOT NULL,
    sex CHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS quest_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pcl5result INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS forum_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_id INTEGER NOT NULL, 
    title VARCHAR(500),
    content VARCHAR(1000),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS forum_replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    og_post_id INTEGER NOT NULL,
    content VARCHAR(1000), 
    FOREIGN KEY (user_id) REFERENCES users(id)
    FOREIGN KEY (og_post_id) REFERENCES forum_posts(id)
);