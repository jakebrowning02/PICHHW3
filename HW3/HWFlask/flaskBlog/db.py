import sqlite3

import click
from flask import current_app, g

#initiates interactions with database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        
    return g.db
    
#closes database if the database is open
def close_db(e=None):
    db = g.pop('db',None)
    
    if db is not None:
        db.close()

#initiates the database
def init_db():
    db = get_db()
    
    with current_app.open_resource('schematic.sql') as f:
        db.executescript(f.read().decode('utf8'))

#command for initiating the database
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

#closes database when app initiated and adds command for initiating database
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
