from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import memcache

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

mc = memcache.Client(['127.0.0.1:11211'])

from app import views, models
