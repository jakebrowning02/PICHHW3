from flask import(
        Blueprint, flash, g, redirect, render_template, request, url_for
)

from flaskBlog.db import get_db, close_db

bp = Blueprint('blog', __name__)

#defines what is to be shown on the very first page, set it to show all posts for ease of use
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT author, body'
        ' FROM post p'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

#defines the insert message function, inserting the message and author the user inputted into the database and sends us back to the main page
@bp.route('/submit', methods=('GET','POST'))
def insert_message():
    if request.method == 'POST':
        message = request.form['message']
        author = request.form['author']
        error = None
    
        if not message:
            error = 'Message is required.'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                    'INSERT INTO post (author, body)'
                    ' VALUES (?, ?)',
                    (author, message)
            )
            db.commit()
        return redirect(url_for('blog.index'))
        
    return render_template('blog/submit.html')

#selects n random messages from the database, displaying them in a random order
def random_messages(n):
    db = get_db()
    # Fetch n random messages from the database
    messages = db.execute('SELECT author, body FROM post ORDER BY RANDOM() LIMIT ?', (n,)).fetchall()
    #messages = db.fetchall()

    close_db()

    return messages
    
#defines the view page in which the user tells the blog how many messages they wish to see, then to be redirected to the page in which they view the random messages
@bp.route('/view',methods=('GET','POST'))
def view():
    if request.method=='POST':
        num = request.form.get('num', False)
        error = None
        
        if not num:
            error = 'Number is required.'
            
        if error is not None:
            flash(error)
        else:
            messages = random_messages(num)
            return redirect(url_for('blog.randomview', num_messages = num))
    
    return render_template('blog/view.html')

#displays the random messages, with the amount of messages  determined by the previous page
@bp.route('/randomview', methods=('GET', 'POST'))
def randomview():
    n = int(request.args.get('num_messages'))
    messages = random_messages(n)

    # Render the view template with the random messages
    return render_template('blog/randomview.html', messages=messages)
        
    
    
        
