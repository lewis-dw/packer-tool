# dunder variables
__version__ = '1.3.9' # semantic versioning [MAJOR|MINOR|PATCH]
__author__ = 'Lewis Rumsby'
__email__ = 'lewis@driftworks.com'


# import the create_app function from __init__.py
from app import create_app


# if running in main program then allow the app to run
if __name__ == '__main__':
    # run the app
    app = create_app()
    app.run(host='0.0.0.0', ssl_context=('ssl/cert.pem', 'ssl/key.pem'), debug=True)


"""
AVAILABLE AT:
https://local.dwtool.com:5000
https://localhost:5000
https://10.10.66.192:5000
https://127.0.0.1:5000
"""