import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from app import create_app, db
# from app.models import User

app = create_app()
with app.app_context():
    db.create_all()