#! env/bin/python

import os
import cherrypy
from cherrypy.process.plugins import Autoreloader

# our app
from bosphorus import create_app

env = os.environ.get('BOSPHORUS_ENV', 'dev')
app = create_app('bosphorus.settings.{}Config'.format(env.capitalize()), env=env)

if __name__ == '__main__':

    # Mount the application
    cherrypy.tree.graft(app, "/")

    # Unsubscribe the default server
    cherrypy.server.unsubscribe()

    # Autoreload, only for DEBUG
    if env.lower() == 'dev':
        Autoreloader(cherrypy.engine).subscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    # Configure the server object
    server.socket_host = "0.0.0.0"
    server.socket_port = 80
    server.thread_pool = 30

    # For SSL Support
    # server.ssl_module            = 'pyopenssl'
    # server.ssl_certificate       = 'ssl/certificate.crt'
    # server.ssl_private_key       = 'ssl/private.key'
    # server.ssl_certificate_chain = 'ssl/bundle.crt'

    # Subscribe this server
    server.subscribe()

    # Start the server engine (Option 1 *and* 2)

    cherrypy.engine.start()
    cherrypy.engine.block()
