from urlparse import urlparse, urljoin
from flask import request, url_for
from flask.ext.cache import Cache
from celery import Celery


####################
# celery (tasks)
####################

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

#####################
# cache
#####################

cache = Cache()

#####################
# routing helpers
#####################

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


##################
# jinja filters  #
##################

def format_date(date, format='%m/%d/%Y'):
    """ filter for date in jinja2 """
    if date is not None:
        return "%02d/%02d/%04d" % (date.month, date.day, date.year)
    else:
        return ''

def get_base_url(url):
    return url.split('/')[1]

jinja_filters = [
    ('format_date', format_date),
    ('get_base_url', get_base_url)
]
