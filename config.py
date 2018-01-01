import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True
SECRET_KEY = 'jättehemlig'

OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '882846015207964',
        'secret': '92ada4a2a1c58a84a60b2a64ff6fde67'
        },
    'twitter': {}
    }

# mail server settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'npc.zyntabsoft@gmail.com'
MAIL_PASSWORD = 'akepwobhvdzcmwjg'

# administrator list
ADMINS = ['npc.zyntabsoft@gmail.com',
          'viktor.almen@gmail.com']
