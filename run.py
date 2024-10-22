# dunder variables
__version__ = '0.1.0' # semantic versioning [MAJOR|MINOR|PATCH]
__author__ = 'Lewis Rumsby'
__email__ = 'lewis@driftworks.com'


# import to create app
from app import create_app

# create app
app = create_app()

# if running in main program then allow the app to run
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

