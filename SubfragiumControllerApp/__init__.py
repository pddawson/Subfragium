from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os
import logging

db = SQLAlchemy()


def create_app():

    app = Flask(__name__)

    dbPath = os.path.join(app.root_path, 'SubfragiumDB.sqlite3')

    app.config.update(dict(SQLALCHEMY_DATABASE_URI='sqlite:///' + dbPath))
    app.config.update(dict(SQLALCHEMY_TRACK_MODIFICATIONS=False))

    return app


def configureApp(app, cfg):

    app.config.update(dict(SQLALCHEMY_DATABASE_URI=cfg['general']['dbPath']))

    errHandler = logging.FileHandler(cfg['general']['logFile'])
    errHandler.setFormatter(logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s'))
    errHandler.setLevel(cfg['general']['logLevel'].upper())
    app.logger.addHandler(errHandler)
    app.logger.setLevel(cfg['general']['logLevel'].upper())

    lg = logging.getLogger('SubfragiumDBLib')
    lg.setLevel(cfg['general']['logLevel'].upper())
    lg.addHandler(errHandler)
