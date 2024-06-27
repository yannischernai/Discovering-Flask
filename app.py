import sqlite3
from flask import *
from werkzeug.exceptions import abort
from hashlib import sha256
from http import cookies
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    ## recupère des information de la base de donné
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def is_authenticated():
    token = request.cookies.get('token')
    if token:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM user WHERE token = ?', (token,)).fetchone()
        conn.close()
        if user :
            return True
    return False
   

@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('user_login'))
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

##
## POSTS
##

@app.route('/post/<int:post_id>')
def post_get(post_id):
    if not is_authenticated():
        return redirect(url_for('user_login'))
    post = get_post(post_id)
    return render_template('post/get.html', post=post)


@app.route('/post/create', methods=('GET', 'POST'))
def post_create():
    if not is_authenticated():
        return redirect(url_for('user_login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('post/create.html')


@app.route('/post/<int:id>/edit', methods=('GET', 'POST'))
def post_edit(id):
    if not is_authenticated():
        return redirect(url_for('user_login'))
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('post/edit.html', post=post)

@app.route('/post/<int:id>/delete', methods=('POST',))
def post_delete(id):
    if not is_authenticated():
        return redirect(url_for('user_login'))

    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

##
## USER
##

@app.route('/user/login', methods=('GET',))
def logout():
    
    token = request.cookies.get('token')
    conn = get_db_connection()
    conn.execute('UPDATE user SET token = ? WHERE token = ?',(None, token))
    conn.commit()
    conn.close()
    return render_template('user/login.html')
    
@app.route('/user/login', methods=('GET', 'POST'))
def user_login():
    if is_authenticated():
        return redirect(url_for('index'))

    if request.method == 'POST':
        ## information tirer du html de ce que l'utilisateur a ecris
        username = request.form["username"].replace("'", "\\'")
        password = request.form['password']

        if not username and not password:
            flash('username and passwolrd is required')
        elif not username:
            flash('username is required!')
        elif not password:
            flash('password is required!')
        elif not username and not password:
            flash('username en passwolrd is required')
        else:
            conn = get_db_connection()
            # user = conn.execute('SELECT * FROM user WHERE username = ? and password = ?',(username, (sha256(password.encode('utf-8')).hexdigest()))).fetchone()
            
            user = conn.execute(f"SELECT * FROM user WHERE username = '{username}' and password = '{sha256(password.encode('utf-8')).hexdigest()}'").fetchone()
            conn.close()
            ## verifation de user si il est vide alors erreur si il est rempli alor ca marche
            if user:
                token = secrets.token_urlsafe(64)
                conn = get_db_connection()
                conn.execute('UPDATE user SET token = ? WHERE id = ?',(token, user["id"]))
                conn.commit()
                conn.close()
                response = make_response(redirect(url_for('index')))
                response.set_cookie( "token", token )
                return response
            else:
                flash('Username ou mot de passe incorrect')
    return render_template('user/login.html')
