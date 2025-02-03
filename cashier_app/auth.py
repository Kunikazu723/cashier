from flask import (
    Blueprint, render_template, request, redirect, session, g, flash, url_for
)

from werkzeug.security import generate_password_hash, check_password_hash
import re
import functools
from cashier_app.db import get_db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # T0D0
    # Log the user in
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username or not password:
            error = 'Dados inválidos'
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        if not user:
            error = f'Usuário {username} não existe'
        elif not check_password_hash(user['hashpass'], password):
            error = 'Senha incorreta'
        
        if not error:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)

    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # T0D0
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        error = None
        if not username or not password or not confirm:
            error = 'Dados inválidos'
        if password != confirm:
            error = 'Senha e confirmação diferentes'
        
        validRegexPassword = re.compile(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}')
        validEmail = re.compile(r'^.+@\w{3,63}\.\w{2,3}(.\w{2})?')
        if not validRegexPassword.fullmatch(password):
            error = r'Senha fraca, requisitos: 1 maiuscula, 1 numero, 8 caracteres'

        if not validEmail.fullmatch(username):
            error = 'Email inválido'


        if error is None:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO users (username, hashpass) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                )
                db.commit()
                print(f"usuário {username} registrado")
            except db.IntegrityError:
                error = 'Nome de usuário já registrado'
            else:
                return redirect(url_for('auth.login'))
        else:
            flash(error)
    return render_template('auth/register.html')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if not user_id:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
