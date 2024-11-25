from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Import and register blueprints
    from app.default import default
    from app.orders import orders
    app.register_blueprint(default, url_prefix='/')
    app.register_blueprint(orders, url_prefix='/orders')

    # Global 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app