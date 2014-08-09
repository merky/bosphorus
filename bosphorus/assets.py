from flask_assets import Bundle

common_css = Bundle(
    'css/vendor/bootstrap.min.css',
    'css/vendor/font-awesome.min.css',
    'css/vendor/typelate.css',
    'css/vendor/helper.css',
    'css/vendor/select2-bootstrap.css',
    'css/main.css',
    filters='cssmin',
    output='css/common.css'
)

common_js = Bundle(
    'js/vendor/jquery.min.js',
    'js/vendor/bootstrap.min.js',
    'js/vendor/select2.min.js',
    Bundle(
        'js/main.js',
        filters='jsmin'
    ),
    output='js/common.js'
)

