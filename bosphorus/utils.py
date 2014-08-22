from functools import wraps
from urlparse import urlparse, urljoin
from flask import request, url_for, Response, stream_with_context, redirect
from flask import Blueprint, current_app
from flask.ext.cache import Cache
from flask.ext.login import current_user
import requests

#####################
# cache
#####################

cache = Cache()

#####################
# decorators
#####################

def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not current_user.is_authenticated() or not current_user.is_admin():
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorator

def modify_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not current_user.is_authenticated() or not current_user.can_edit():
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorator


#####################
# proxy images
#####################

proxy = Blueprint('proxy', __name__, url_prefix='/serve')

@cache.cached(timeout=300)
@proxy.route('/img/<instance_id>')
def img(instance_id):
    url = '/'.join([current_app.config['ORTHANC_URI'],
                   'instances',
                   instance_id,
                   'preview'])
    req = requests.get(url, stream=True)
    #return Response(url, mimetype='text/xml')
    return Response(stream_with_context(req.iter_content()),
                    content_type = req.headers['content-type'])


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

jinja_filters = [
    ('format_date', format_date),
]
