DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS history;

CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        hashpass TEXT NOT NULL
    );

CREATE UNIQUE INDEX idx_id_username ON users(id, username);

CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price NUMERIC NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
CREATE UNIQUE INDEX idx_prdct_uid ON products (product_name, user_id);

CREATE TABLE history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        unit_price NUMERIC NOT NULL,
        total NUMERIC NOT NULL,
        time TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
CREATE UNIQUE INDEX idx_time_id ON history (time, id);