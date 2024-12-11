# logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from app import create_app, db
from app.models import Orders

what_to_do = 'create_all'
delete_table = 'test_orders'

app = create_app()
with app.app_context():
    # create all tables imported
    if what_to_do == 'create_all':
        db.create_all()

    # delete specified table
    elif what_to_do == 'delete':
        db.metadata.tables[delete_table].drop(db.engine)