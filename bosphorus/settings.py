import os

DEBUG = False

# secret key
SECRET_KEY  = os.environ.get('SECRET_KEY', 'the secret key')



# database
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'bosphorus')
DB_USER = os.environ.get('DB_USER', 'bosphorus')
DB_PASS = os.environ.get('DB_PASS', 'bosphorus-password')

SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db}?charset=utf8&use_unicode=0'.format(
                                user     = DB_USER,
                                password = DB_PASS,
                                host     = DB_HOST,
                                db       = DB_NAME
                           )
# orthanc

ORTHANC_HOST  = os.environ.get('ORTHANC_HOST', 'localhost')
ORTHANC_URI = 'http://%s:8042' % ORTHANC_HOST

# redis
REDIS_HOST  = os.environ.get('REDIS_HOST', 'localhost')

### CELERY ####

CELERY_BROKER_URL = 'redis://%s:6379/0' % REDIS_HOST
BROKER_URL = CELERY_BROKER_URL
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_SERIALIZER = 'json'

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'update-studies-every-15-seconds': {
        'task': 'task.update_studies',
        'schedule': timedelta(seconds=15)
    },
    'clean-studies-every-30min': {
        'task': 'task.clean_studies',
        'schedule': timedelta(minutes=30)
    },
}
CELERY_TIMEZONE = 'UTC'

####

CACHE_TYPE = 'simple'

# This allows us to test the forms from WTForm
WTF_CSRF_ENABLED = True

