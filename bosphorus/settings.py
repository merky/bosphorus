import os
filedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'secret key'


class ProdConfig(Config):
    dbpath = os.path.join(filedir,'../database.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(dbpath)

    ORTHANC_URI = 'http://localhost:8042'

    CACHE_TYPE = 'simple'


class DevConfig(Config):
    DEBUG = True

    dbpath = os.path.join(filedir,'../database.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(dbpath)
    SQLALCHEMY_ECHO = True

    ORTHANC_URI = 'http://localhost:8042'

    CACHE_TYPE = 'null'

    # This allows us to test the forms from WTForm
    WTF_CSRF_ENABLED = False
