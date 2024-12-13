# logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from sqlalchemy.schema import CreateTable
from app import create_app, db
from app.shipper.shipping_functions import get_all_yamls
import os
import pathlib


from app.models import Outs


cur_dir = pathlib.Path(__file__).parent
data_dir = os.path.join(cur_dir, 'data')



def drop_table(table_name):
    db.metadata.tables[table_name].drop(db.engine)


def create_table(table_name):
    db.metadata.tables[table_name].create(db.engine)


def save_table(table_name):
    orders_table = db.metadata.tables[table_name]
    create_statement = str(CreateTable(orders_table).compile(db.engine))
    rows = db.session.query(Outs).all() # THIS NEEDS TO BE CHANGED TO THE IMPORTED TABLE

    # Prepare INSERT statements for each row
    insert_statements = []
    for row in rows:
        insert_statement = f"INSERT INTO orders ({', '.join(orders_table.columns.keys())}) VALUES ({', '.join([repr(getattr(row, col)) for col in orders_table.columns.keys()])});"
        insert_statements.append(insert_statement)

    # write schema and data
    with open(os.path.join(data_dir, f'{table_name}_schema.sql'), 'w') as f:
        f.write(create_statement + ";\n\n")
        f.write("\n".join(insert_statements))



app = create_app()
table_name = 'outs'

with app.app_context():
    """Perform a function"""
    # drop_table(table_name)
    create_table(table_name)