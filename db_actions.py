# logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from sqlalchemy.schema import CreateTable
from app import create_app, db
import os
import pathlib

# table to create
from app.models import ProductOptions, CommodityCodes


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



codes = [
    '27101987',
'27101999',
'38200000',
'39199000',
'39269097',
'40111000',
'58101090',
'61091000',
'61102091',
'69111000',
'73181300',
'73181569',
'73181650',
'73181691',
'73202081',
'84099100',
'84241000',
'84241000',
'84241000',
'85234951',
'87081090',
'87081090',
'87082990',
'87082990',
'87082990',
'87083091',
'87083099',
'87085091',
'87085099',
'87087050',
'87087099',
'87087099',
'87088055',
'87088099',
'87088099',
'87089135',
'87089235',
'87089310',
'87089435',
'87089499',
'90318038'
]

names = [
    'Gearbox/LSD Oil',
'Motor Oil',
'Water Wetter/Slip Diff Friction Modifier',
'Stickers',
'Cable ties',
'Tyres',
'Driftworks Patches/Lanyards',
'Tshirt',
'Hoody',
'tea coffee mug',
'Harness eyebolt',
'Bucket seat mounting bolts',
'M8 metal locking nut',
'Eyebolt mounting plate',
'Springs',
'hoses/filers/socks/spark plugs/boost guage/general engine',
'Fire Safty, Balaclava, extinguishers, pull cable etc',
'Seats',
'Harness/Tow Hooks/',
'Outsiders Collectors Box Set DVD & Blu-Ray',
'Bonnet pins',
'Super Wide Carbon Fibre 3D Wing',
'Seatrails',
'Gearknobs and Gaters',
'Braille Vertical Battery Mount Kit',
'Handbreaks/lines/pads etc',
'handbrake button',
'Arms & Knuckles. Wisefab/Geomaster',
'LSD',
'Wheels',
'Wheel nuts and Spacers',
'Bushes',
'Coilovers & Anti-Roll Bar',
'Arms',
'Bushes',
'Radiators',
'Gaskets/exhaust wrap',
'Flywheel & Clutches',
'Steering Wheels',
'Hubs/Bosses/bushes/Rack Spacers/PCD Adapter',
'Boost Gauge'
]

def add_row():
    for code, name in zip(codes, names):
        CommodityCodes.add_row(
            code,
            name
        )

app = create_app()
table_name = CommodityCodes.__tablename__


with app.app_context():
    """Perform a function"""
    # drop_table(table_name)
    create_table(table_name)

    add_row()