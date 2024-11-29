from flask import Flask, render_template, send_from_directory, g
from flask_talisman import Talisman
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Metadata variables
__version__ = '1.5.0'  # Semantic versioning: [MAJOR|MINOR|PATCH]
__author__ = 'Lewis Rumsby'
__email__ = 'lewis@driftworks.com'


def create_app():
    """
    Factory function to create and configure the Flask application
    """
    # create flask app and load config
    app = Flask(__name__)
    app.config.from_object('config.Config')


    # set secret key for session variables
    app.secret_key = os.getenv('SECRET_KEY')


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
    serve_manifest(app)
    return app


def register_blueprints(app):
    """
    Register Flask blueprints
    """
    from app.default import default
    from app.orders import orders
    from app.shipping import shipping

    app.register_blueprint(default, url_prefix='/')
    app.register_blueprint(orders, url_prefix='/orders')
    app.register_blueprint(shipping, url_prefix='/shipping')


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


def serve_manifest(app):
    """
    Add custom routes for specific files or endpoints
    """
    @app.route('/manifest.json')
    def manifest():
        return send_from_directory('static', 'manifest.json')
