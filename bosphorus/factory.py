import os

from flask import Flask
from flask_assets import Environment
from webassets.loaders import PythonLoader as PythonAssetsLoader
from celery import Celery

from bosphorus import assets
from bosphorus.models import db, orthanc
from bosphorus.utils  import jinja_filters, cache


def create_app(object_name, env='dev'):

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

    #init Orthanc
    orthanc.init_app(app)

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
    from utils import proxy
    app.register_blueprint(main)
    app.register_blueprint(user)
    app.register_blueprint(person)
    app.register_blueprint(studies)
    app.register_blueprint(proxy)

    return app


def create_celery_app(app=None):
    app = app or create_app('bosphorus.settings', env='prod')
    celery = Celery(app.import_name,app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

