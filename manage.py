#!env/bin/python
import os

from flask.ext.script import Manager, Server
from bosphorus import create_app
from bosphorus.models import db, User, ResearchID, Person

env = os.environ.get('BOSPHORUS_ENV', 'dev')
app = create_app('bosphorus.settings.%sConfig' % env.capitalize(), env=env)

manager = Manager(app)
manager.add_command("server", Server(port=80))

@app.template_filter()
def format_date(date, format='%m/%d/%Y'):
    """ filter for date in jinja2 """
    if date is not None:
        return "%02d/%02d/%04d" % (date.month, date.day, date.year)
    else:
        return ''


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """

    return dict(app=app, User=User)


@manager.command
def createdb():
    """ Creates a database with all of the tables defined in
        your Alchemy models
    """

    db.create_all()

@manager.command
def resetdb():
    db.drop_all()

def init_ids(idfile):
    """ Inserts default values of possible research IDs.
    """
    # read file
    with open(idfile, 'r') as f:
        ids = f.read().splitlines()

    # insert into DB
    for id in ids:
        db.session.add(ResearchID(id))
    db.session.commit()


def init_users():
    admin = User('admin','admin','hollenbeck.mark@gmail.com')
    db.session.add(admin)
    db.session.commit()


@manager.command
@manager.option('--idfile', help='File with possible IDs separated by newlined')
def initdb(idfile):
    """ Sets up default values and admin account
    """
    resetdb()
    createdb()
    init_ids(idfile)
    init_users()


if __name__ == "__main__":
    manager.run()
