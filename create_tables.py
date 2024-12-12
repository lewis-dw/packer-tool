# logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from app import create_app, db
from app.models import Countries
from app.shipper.shipping_functions import get_all_yamls


def create_table(table_name):
    pass


def drop_table(table_name):
    db.metadata.tables[table_name].drop(db.engine)


def populate_countries():
    # country code load
    country_codes = get_all_yamls('country_codes')

    for key, val in country_codes.items():
        row = Countries(
            country_name=key,
            country_code=val,
            shipping_country_code=val,
            etd_required=True
        )
        db.session.add(row)
        db.session.commit()


app = create_app()
table_name = ''

with app.app_context():
    """Perform a function"""
    populate_countries()