import datetime

from os import path


# App details
BASE_DIRECTORY = path.abspath(path.dirname(__file__))
DEBUG = True
SECRET_KEY = ''

# Database details
SQLALCHEMY_DATABASE_URI = '{0}{1}'.format('sqlite:///',
                                          path.join(BASE_DIRECTORY, 'app.db'))

DEFAULT_TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))

FB_APP_ID = ''
FB_APP_NAME = ''
FB_APP_SECRET = ''

