import sqlite3
from hashlib import sha256
from http import cookies

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )
             
             
cur.execute("INSERT INTO user (username, password) VALUES (?, ?)",
            ("yannis", (sha256("code".encode('utf-8')).hexdigest()))
            )

connection.commit()
connection.close()