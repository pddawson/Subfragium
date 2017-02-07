from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import os
import logging

db = SQLAlchemy()


def create_app():

    app = Flask(__name__)

    dbPath = os.path.join(app.root_path, 'SubfragiumDB.sqlite3')

    app.config.update(dict(SQLALCHEMY_DATABASE_URI='sqlite:///' + dbPath))
    app.config.update(dict(SQLALCHEMY_TRACK_MODIFICATIONS=False))

    errHandler = logging.FileHandler('SubfragiumController.log')
    errHandler.setFormatter(logging.Formatter('%(asctime)s,%(levelname)s,%(message)s'))
    errHandler.setLevel(logging.INFO)
    app.logger.addHandler(errHandler)
    app.logger.setLevel(logging.DEBUG)

    return app
