#!env/bin/python

import os
from flask import render_template
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
from bosphorus import create_app
from bosphorus.models import db, User, ResearchID, Person, Study, orthanc
from wsgi import create_cherrypy

env = os.environ.get('BOSPHORUS_ENV', 'dev')
app = create_app(env=env)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
manager.add_command("testserver", Server(port=80))


@app.before_request
def check_orthanc(*args, **kwargs):
    if not orthanc.ready():
        msg = "It appears there is a problem connecting to Orthanc."
        return render_template('error.html',message=msg)


@manager.command
def server():
    """ starts wsgi server """
    create_cherrypy(app)


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """
    return dict(app=app,
                db=db,
                Person=Person,
                Study=Study,
                ResearchID=ResearchID)

@manager.command
def createdb():
    """ create db """
    db.create_all(app=app)

@manager.command
def init_ids(idfile='fake_names.txt'):
    """ Inserts default values of possible research IDs.
    """
    # read file
    with open(idfile, 'r') as f:
        ids = f.read().splitlines()

    # insert into DB
    for id in ids:
        rid = ResearchID(research_id=id,
                         used=False)
        db.session.add(rid)
    db.session.commit()

@manager.command
def init_users():
    admin = User(username='admin',
                 password='admin',
                 email   ='user@gmail.com')
    db.session.add(admin)
    db.session.commit()

if __name__ == "__main__":
    manager.run()
