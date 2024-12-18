# logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from sqlalchemy.schema import CreateTable
from app import create_app, db
import os
import pathlib

# table to create
from app.models import ProductOptions


cur_dir = pathlib.Path(__file__).parent
data_dir = os.path.join(cur_dir, 'data')



def drop_table(table_name):
    db.metadata.tables[table_name].drop(db.engine)


def create_table(table_name):
    db.metadata.tables[table_name].create(db.engine)


def save_table(table_name):
    orders_table = db.metadata.tables[table_name]
    create_statement = str(CreateTable(orders_table).compile(db.engine))
    rows = db.session.query(ProductOptions).all() # THIS NEEDS TO BE CHANGED TO THE IMPORTED TABLE

    # Prepare INSERT statements for each row
    insert_statements = []
    for row in rows:
        insert_statement = f"INSERT INTO orders ({', '.join(orders_table.columns.keys())}) VALUES ({', '.join([repr(getattr(row, col)) for col in orders_table.columns.keys()])});"
        insert_statements.append(insert_statement)

    # write schema and data
    with open(os.path.join(data_dir, f'{table_name}_schema.sql'), 'w') as f:
        f.write(create_statement + ";\n\n")
        f.write("\n".join(insert_statements))




def add_row():
    description_translate = {
        '"Please Enter Your Car Make/Model/Year so we can provide the correct Spigot Rings (if needed). We won\'t check wheel fitment - so if you\'re unsure on sizes just get in touch!":':'<strong>Provided Car: </strong>',
        'Step 1 - Start by choosing your PCD:':'<strong>PCD: </strong>',
        'Step 2 - Choose your Wheel Diameter:':'<strong>Wheel Diameter: </strong>',
        'Step 3 - Choose your Wheel Width:':'<strong>Wheel Width: </strong>',
        'Step 4 - What offset do you want?:':'Offset:',
        'Step 5 - What disk type do you want?:':'Disk Type:',
        'Step 5a - What brake setup are you running?:':'Brake Setup:',
        'Step 6 - Choose your Centre Colour:':'Centre Colour:',
        'Step 7 - choose your Lip Colour:':'Lip Colour:',
        'Step 8 - Choose Your Assembly Bolt Colour:':'Assembly Bolt Colour:',
        'WORK WHEEL SHIPPING METHOD:':'Work Wheel Shipping Method:'
    }

    for f, r in description_translate.items():
        db.session.add(ProductOptions(
            find_this=f,
            replace_with=r
        ))
    db.session.commit()


app = create_app()
table_name = ProductOptions.__tablename__



with app.app_context():
    """Perform a function"""
    # drop_table(table_name)
    # create_table(table_name)

    # add_row()