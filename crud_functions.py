import sqlite3
def initiate_db():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect('Users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            balance INTEGER NOT NULL DEFAULT 1000
        )
    ''')
    conn.commit()
    conn.close()
def get_all_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    conn.close()
    return products

def add_user(username, email, age):
    conn = sqlite3.connect('Users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)", (username, email, age, 1000))
    conn.commit()
    conn.close()

def is_included(username):
    conn = sqlite3.connect('Users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return True if result else False

initiate_db()
