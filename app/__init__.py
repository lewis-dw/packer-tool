# metadata variables
__version__ = '1.15.1'  # semantic versioning: [MAJOR|MINOR|PATCH]
__author__ = 'Lewis Rumsby'
__email__ = 'lewis@driftworks.com'


# imports
from flask import Flask, render_template, send_from_directory, g
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
import os
import re
from dotenv import load_dotenv


# load environment variables
load_dotenv()

# create the database
db = SQLAlchemy()


# create the shipper objects (below load_dotenv)
from app.shipper import fedex_class, ups_class, royal_mail_class
fedex = fedex_class.FedEx()
ups = ups_class.UPS()


def create_app():
    """
    Factory function to create and configure the Flask application
    """
    # create flask app
    app = Flask(__name__)


    # load up the config and env vars
    app.config.from_object('config.Config') # app config
    app.secret_key = os.getenv('SECRET_KEY') # secret key for session storage


    # initialize db extensions
    db.init_app(app)


    # configure Talisman for security
    Talisman(
        app,
        force_https=True,
        content_security_policy=None
    )


    # run the other setup functions then return the app instance
    register_blueprints(app)
    set_global_variables(app)
    link_error_pages(app)
    create_custom_filter(app)
    serve_manifest(app)
    return app


def register_blueprints(app):
    """
    Register Flask blueprints
    """
    from app.default import default
    from app.orders import orders
    from app.shipping import shipping
    from app.purchases import purchasing

    app.register_blueprint(default, url_prefix='/')
    app.register_blueprint(orders, url_prefix='/orders')
    app.register_blueprint(shipping, url_prefix='/shipping')
    app.register_blueprint(purchasing, url_prefix='/purchases')


def set_global_variables(app):
    """
    Set up global variables in `g` object to be accessible in request context
    """
    @app.before_request
    def before_request():
        g.version = __version__
        g.author = __author__
        g.email = __email__


def link_error_pages(app):
    """
    Register global error handlers for the application
    """
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404


def create_custom_filter(app):
    """
    Create custom filter for filtering html in the Jinja2 template
    """
    @app.template_filter('strip_html')
    def strip_html_filter(text):
        clean_text = re.sub(r'<.*?>', ' ', text)
        clean_text = re.sub(r' +', ' ', clean_text).strip()
        return clean_text


def serve_manifest(app):
    """
    Add custom routes for specific files or endpoints
    """
    @app.route('/manifest.json')
    def manifest():
        return send_from_directory('static', 'manifest.json')