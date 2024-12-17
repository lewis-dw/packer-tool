from app import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import MEDIUMBLOB



# class ShippingHistory(db.Model):
#     __tablename__ = 'shipping_history'
#     id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
#     order_name = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL

#     date_shipped = db.Column(db.DateTime(timezone=True), nullable=True, default=func.now()) # DATETIME
#     name = db.Column(db.String(64), nullable=False) # VARCHAR(64) NOT NULL
#     company = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL
#     customer_paid = db.Column(db.Numeric(10, 2), nullable=False) # NUMERIC(10, 2) NOT NULL
#     dw_paid = db.Column(db.Numeric(10, 2), nullable=False) # NUMERIC(10, 2) NOT NULL
#     tracking_number = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
#     courier = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
#     method = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL


#     def __repr__(self):
#         return f'<Order {self.order_name}>'



# class Picks(db.Model):
#     __tablename__ = 'picks'
#     id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
#     order_name = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
#     pick_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL

#     def __repr__(self):
#         return f'<Pick ID {self.pick_id}>'




# class Packs(db.Model):
#     __tablename__ = 'packs'
#     id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
#     order_name = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
#     pack_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL

#     def __repr__(self):
#         return f'<Pack ID {self.pack_id}>'


#################################################################################################################################################
# Shipping Results


class Outs(db.Model):
    __tablename__ = 'outs'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    order_name = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    out_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    processed_at = db.Column(db.DateTime(timezone=True), nullable=True, default=func.now()) # DATETIME
    name = db.Column(db.String(64), nullable=False) # VARCHAR(64) NOT NULL
    company = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL
    shipped_to = db.Column(db.String(128), nullable=False) # VARCHAR(81280) NOT NULL
    customer_paid = db.Column(db.Numeric(10, 2), nullable=False) # NUMERIC(10, 2) NOT NULL
    dw_paid = db.Column(db.Numeric(10, 2), nullable=False) # NUMERIC(10, 2) NOT NULL
    tracking_number = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    courier = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    method = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL
    commercial_invoice = db.Column(MEDIUMBLOB, nullable=True) # MEDIUMBLOB NULL

    def __repr__(self):
        return f'<Out ID {self.out_id}>'


#################################################################################################################################################
# General Data


class Countries(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    country_name = db.Column(db.String(64), nullable=False) # VARCHAR(64) NOT NULL
    country_code = db.Column(db.String(4), nullable=False) # VARCHAR(4) NOT NULL
    shipping_country_code = db.Column(db.String(4), nullable=False) # VARCHAR(4) NOT NULL
    etd_required = db.Column(db.Boolean, nullable=False) # BOOLEAN NOT NULL
    sat_indicator = db.Column(db.Boolean, nullable=False) # BOOLEAN NOT NULL

    def __repr__(self):
        return f'<Country {self.country_name}>'


class ShippingFlags(db.Model):
    __tablename__ = 'shipping_flags'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    country_code = db.Column(db.String(4), nullable=False) # VARCHAR(4) NOT NULL
    flag_svg = db.Column(db.Text, nullable=False)  # TEXT NOT NULL

    def __repr__(self):
        return f'<Country ID {self.country_code}>'




class ShippingCodes(db.Model):
    __tablename__ = 'shipping_codes'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    shipping_code = db.Column(db.String(128), nullable=False) # VARCHAR(128) NOT NULL
    friendly_code = db.Column(db.String(128), nullable=False) # VARCHAR(128) NOT NULL

    def __repr__(self):
        return f'<Shipping Code {self.friendly_code}>'




class Printers(db.Model):
    __tablename__ = 'printer_info'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    server_name = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    printer_name = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    can_print_4x6 = db.Column(db.Boolean, nullable=False) # BOOLEAN NOT NULL
    can_print_4x675 = db.Column(db.Boolean, nullable=False) # BOOLEAN NOT NULL

    def __repr__(self):
        return f'<Printer UNC \\{self.server_name}\{self.printer_name}>'