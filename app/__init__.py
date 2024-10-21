from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .routes import main

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    
    # load config settings
    app.config.from_object('config.Config')

    # init app
    db.init_app(app)

    # import and register blueprints/routes
    app.register_blueprint(main)

    return app
