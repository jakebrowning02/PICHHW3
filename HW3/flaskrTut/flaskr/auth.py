import functools

from flask import(Blueprint, flash, g, redirect, render_template, request, url_for, session)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

#creates blueprint named 'auth', where the url prefix will be prepended to all the URLs associated with this blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

#associates URL segment '/register' with this register function
@bp.route('/register', methods=('GET','POST'))
def register():
    if request.method == 'POST':
        #user enters their desired username and password
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        #checks that username and password are not empty, redefines error if they are
        if not username:
            error = 'Username is required.'
        elif not password:
            error= 'Password is required.'
            
        if error is None:
            #inserts the user input into the database, using hash to securely store password
            try:
                db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password)),
                )
                db.commit()
            #this checks if the username already exists, and if it does it sends the user to the login page
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        #error shown to user if there is an error
        flash(error)
    
    #renders the template for this register page
    return render_template('auth/register.html')
    
#associates URL segment '/login' with this login function
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        #user enters their username and password
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        #checks if username is in database, redefining error if it does not exist
        if user is None:
            error = 'Incorrect username.'
        #checks if password of username matches the password entered by the user
        elif not check_password_hash(user['password'],password):
            error = 'Incorrect password.'
        
        #user's id stored in new session
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        #flashes error if validation fails
        flash(error)
    #renders the template for this login page
    return render_template('auth/login.html')

#function tries to load user who is still logged in
@bp.before_app_request
def load_logged_in_user():
    #checks session for user id
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        
#function to logout user previously logged in
@bp.route('/logout')
def logout():
    #clears session which removes user id, stopping load_logged_in_user() from logging back in logged out users
    session.clear()
    return redirect(url_for('index'))

#checks to make sure someone is logged in
def login_required(view):
    @functools.wraps(view)
    #checks if there is a logged in user
    def wrapped_view(**kwargs):
        #redirects to login page if no user is logged in
        if g.user is None:
            return redirect(url_for('auth.login'))
            
        return view(**kwargs)
        
    return wrapped_view

