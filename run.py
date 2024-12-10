# import the create_app function from __init__.py
from app import create_app
# from flask import session

# if running in main then create the application and run it
if __name__ == '__main__':
    # create and run the app
    app = create_app()
    app.run(host='0.0.0.0', ssl_context=('ssl/cert.pem', 'ssl/key.pem'), debug=True)


"""
AVAILABLE AT:
https://local.dwtool.com:5000
https://localhost:5000
https://10.10.66.192:5000
https://127.0.0.1:5000
"""