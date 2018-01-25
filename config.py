import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True
SECRET_KEY = os.environ.get('SECRET_KEY') or 'jättehemlig'

OAUTH_CREDENTIALS = {
    'facebook': {
        'id': os.environ.get('FACEBOOK_ID'),
        'secret': os.environ.get('FACEBOOK_SECRET')
        },
    'twitter': {}
    }

# mail server settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['npc.zyntabsoft@gmail.com',
          'viktor.almen@gmail.com']
