from flask import Flask, render_template, send_from_directory
from flask_talisman import Talisman

def create_app():
    # create app
    app = Flask(__name__)
    app.config.from_object('config.Config')


    # talisman settings
    talisman = Talisman(
        app,
        force_https=True,
        content_security_policy=None
        # content_security_policy={
        #     'default-src': '\'self\'',
        #     'manifest-src': '\'self\'',
        #     'worker-src': '\'self\'',
        #     'img-src': '*'
        # }
    )


    # Import and register blueprints
    from app.default import default
    from app.orders import orders
    app.register_blueprint(default, url_prefix='/')
    app.register_blueprint(orders, url_prefix='/orders')


    # Global 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404


    # serve the manifest
    @app.route('/manifest.json')
    def manifest():
        return send_from_directory('static', 'manifest.json')


    # return the app
    return app