# dunder variables
__version__ = '0.1.0' # semantic versioning [MAJOR|MINOR|PATCH]
__author__ = 'Lewis Rumsby'
__email__ = 'lewis@driftworks.com'


# import the create_app function from __init__.py
from app import create_app


# if running in main program then allow the app to run
if __name__ == '__main__':
    # run the app
    app = create_app()
    app.run(debug=True, host='0.0.0.0')

