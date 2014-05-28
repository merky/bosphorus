#!env/bin/python

from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
from bosphorus import auto_app
from bosphorus.models import db, User, ResearchID, Person, Study

app = auto_app()
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("server", Server(port=80))
manager.add_command("db", MigrateCommand)


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
def init_ids(idfile):
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
