import os

from flask import Flask, current_app
from flask_assets import Environment
from flask.ext.login import LoginManager
from webassets.loaders import PythonLoader as PythonAssetsLoader

from bosphorus import assets
from bosphorus.models import db, orthanc
from bosphorus.utils  import jinja_filters, cache
from bosphorus.tasks  import celery

lm = LoginManager()
lm.login_view = 'user.login'

def create_barebones_app(object_name, env):
    app = Flask(__name__)

    # set config
    app.config.from_object(object_name)
    app.config['ENV'] = env
    app.config['DEBUG'] = False if env=="prod" else True

    # register all custom jinja filters
    for f in jinja_filters:
        app.jinja_env.filters[f[0]] = f[1]

    #init the cache
    cache.init_app(app)

    #init SQLAlchemy
    db.init_app(app)

    #init celery 
    celery.config_from_object(app.config)

    #init Orthanc
    orthanc.init_app(app)

    #init logins
    lm.init_app(app)

    return app
    

def create_app(object_name='bosphorus.settings', env='dev'):
    
    app = create_barebones_app(object_name, env)

    # Import and register the different asset bundles
    assets_env = Environment()
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().iteritems():
        assets_env.register(name, bundle)

    # register our blueprints
    from controllers.main import main
    from controllers.user import user
    from controllers.studies import studies
    from controllers.person import person
    from controllers.protocol import protocol
    from utils import proxy
    app.register_blueprint(main)
    app.register_blueprint(user)
    app.register_blueprint(person)
    app.register_blueprint(studies)
    app.register_blueprint(protocol)
    app.register_blueprint(proxy)

    return app


def create_celery_app(app=None):
    from celery import Celery
    app = app or create_barebones_app('bosphorus.settings', env='prod')
    celery = Celery(app.import_name,app.config['CELERY_BROKER_URL'])
    celery.config_from_object(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

