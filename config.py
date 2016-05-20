import os
basedir = os.path.abspath(os.path.dirname(__file__))

# SqlAlchemy Set up
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLACLHEMY_ECHO = True
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Flask set up
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# Authentication details
## OpenID
OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

## OAuth
GOOGLE_LOGIN_CLIENT_ID = "<your-id-ending-with>.apps.googleusercontent.com"
GOOGLE_LOGIN_CLIENT_SECRET = "<your-secret>"

OAUTH_CREDENTIALS={
        'google': {
            'id': GOOGLE_LOGIN_CLIENT_ID,
            'secret': GOOGLE_LOGIN_CLIENT_SECRET
        }
}

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['tanawat.kh@gmail.com']
