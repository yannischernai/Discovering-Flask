import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort


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
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

##
## POSTS
##

@app.route('/post/<int:post_id>')
def post_get(post_id):
    post = get_post(post_id)
    return render_template('post/get.html', post=post)


@app.route('/post/create', methods=('GET', 'POST'))
def post_create():
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
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/user/login', methods=('GET', 'POST'))
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        passworld = request.form['passworld']

        if not username:
            flash('username is required!')
        elif not passworld:
            flash('passworld is required!')
        else:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM user WHERE username = ? and passworld = ?',
                   (username,passworld)).fetchone()
            conn.close()
            if user:
                return redirect(url_for('index'))
            else:
                flash('Username ou mot de passe incorrect')

    return render_template('user/login.html')