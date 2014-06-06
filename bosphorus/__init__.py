#! ../env/bin/python
import os

from flask import Flask
from flask_assets import Environment
from webassets.loaders import PythonLoader as PythonAssetsLoader

from bosphorus import assets
from bosphorus.models import db, orthanc
from bosphorus.utils  import jinja_filters, cache


# init flask assets
assets_env = Environment()

def auto_app():
    env = os.environ.get('BOSPHORUS_ENV', 'prod')
    app = create_app('bosphorus.settings.%sConfig' % env.capitalize(), env=env)
    return app


def create_app(object_name, env="prod"):

    app = Flask(__name__)

    # set config
    app.config.from_object(object_name)
    app.config['ENV'] = env

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
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().iteritems():
        assets_env.register(name, bundle)

    # register our blueprints
    from controllers.main import main
    from controllers.user import user
    from controllers.studies import studies
    from controllers.person import person
    app.register_blueprint(main)
    app.register_blueprint(user)
    app.register_blueprint(person)
    app.register_blueprint(studies)

    return app


if __name__ == '__main__':
    app = auto_app()
    app.run()

