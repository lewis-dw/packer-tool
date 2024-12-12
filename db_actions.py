# logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from sqlalchemy.schema import CreateTable
from app import create_app, db
from app.models import Countries, ShippingCodes
from app.shipper.shipping_functions import get_all_yamls
import os
import pathlib


cur_dir = pathlib.Path(__file__).parent
data_dir = os.path.join(cur_dir, 'data')


def save_countries():
    orders_table = db.metadata.tables['countries']
    create_statement = str(CreateTable(orders_table).compile(db.engine))
    rows = db.session.query(Countries).all()

    # Prepare INSERT statements for each row
    insert_statements = []
    for row in rows:
        insert_statement = f"INSERT INTO orders ({', '.join(orders_table.columns.keys())}) VALUES ({', '.join([repr(getattr(row, col)) for col in orders_table.columns.keys()])});"
        insert_statements.append(insert_statement)

    # write schema and data
    with open(os.path.join(data_dir, f'countries_schema.sql'), 'w') as f:
        f.write(create_statement + ";\n\n")
        f.write("\n".join(insert_statements))


def save_shipping():
    orders_table = db.metadata.tables['shipping_codes']
    create_statement = str(CreateTable(orders_table).compile(db.engine))
    rows = db.session.query(ShippingCodes).all()

    # Prepare INSERT statements for each row
    insert_statements = []
    for row in rows:
        insert_statement = f"INSERT INTO orders ({', '.join(orders_table.columns.keys())}) VALUES ({', '.join([repr(getattr(row, col)) for col in orders_table.columns.keys()])});"
        insert_statements.append(insert_statement)

    # write schema and data
    with open(os.path.join(data_dir, f'shipping_codes_schema.sql'), 'w') as f:
        f.write(create_statement + ";\n\n")
        f.write("\n".join(insert_statements))



def create_table(table_name):
    db.metadata.tables[table_name].create(db.engine)


def drop_table(table_name):
    db.metadata.tables[table_name].drop(db.engine)


def populate_shipping():
    fedex_codes = {
        "01 - Next Day Air - Saturday": "01Yes",
        "02 - 2nd Day Air - Saturday": "02Yes",
        "03 - Ground - Saturday": "03Yes",
        "07 - Express - Saturday": "07Yes",
        "08 - Expedited - Saturday": "08Yes",
        "11 - UPS Standard - Saturday": "11Yes",
        "12 - 3 Day Select - Saturday": "12Yes",
        "13 - Next Day Air Saver - Saturday": "13Yes",
        "14 - UPS Next Day Air® Early - Saturday": "14Yes",
        "17 - UPS Worldwide Economy DDU - Saturday": "17Yes",
        "54 - Express Plus - Saturday": "54Yes",
        "59 - 2nd Day Air A.M. - Saturday": "59Yes",
        "65 - UPS Saver - Saturday": "65Yes",
        "M2 - First Class Mail - Saturday": "M2Yes",
        "M3 - Priority Mail - Saturday": "M3Yes",
        "M4 - Expedited MaiI Innovations - Saturday": "M4Yes",
        "M5 - Priority Mail Innovations - Saturday": "M5Yes",
        "M6 - Economy Mail Innovations - Saturday": "M6Yes",
        "M7 - MaiI Innovations (MI) Returns - Saturday": "M7Yes",
        "70 - UPS Access Point™ Economy - Saturday": "70Yes",
        "71 - UPS Worldwide Express Freight Midday - Saturday": "71Yes",
        "72 - UPS Worldwide Economy - Saturday": "72Yes",
        "74 - UPS Express®12:00 - Saturday": "74Yes",
        "82 - UPS Today Standard - Saturday": "82Yes",
        "83 - UPS Today Dedicated Courier - Saturday": "83Yes",
        "84 - UPS Today Intercity - Saturday": "84Yes",
        "85 - UPS Today Express - Saturday": "85Yes",
        "86 - UPS Today Express Saver - Saturday": "86Yes",
        "96 - UPS Worldwide Express Freight - Saturday": "96Yes",
    }

    for key, val in fedex_codes.items():
        row = ShippingCodes(
            friendly_code=key,
            shipping_code=val
        )
        db.session.add(row)
        db.session.commit()



app = create_app()
table_name = 'shipping_codes'

with app.app_context():
    """Perform a function"""
    # drop_table(table_name)
    # create_table(table_name)


    # populate_shipping()


    # perm functions
    # save_countries()
    # save_shipping()