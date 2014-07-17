import os

DEBUG = True

# secret key
SECRET_KEY  = os.environ.get('SECRET_KEY', 'the secret key')

# db
filedir = os.path.abspath(os.path.dirname(__file__))
default_db = os.path.join(filedir, '..', 'bosphorus.db')

# env vars
DB_LOC  = os.environ.get('DB_LOC', default_db)
ORTHANC_HOST  = os.environ.get('ORTHANC_HOST', 'localhost')
REDIS_HOST  = os.environ.get('REDIS_HOST', 'localhost')

# settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % DB_LOC
SQLALCHEMY_ECHO = True

ORTHANC_URI = 'http://%s:8042' % ORTHANC_HOST

CELERY_BROKER_URL = 'redis://%s:6379' % REDIS_HOST
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

CACHE_TYPE = 'simple'

# This allows us to test the forms from WTForm
WTF_CSRF_ENABLED = True
