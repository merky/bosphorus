from bosphorus.factory import create_app
from bosphorus.tasks   import celery

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        celery.start()
