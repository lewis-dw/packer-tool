from app import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import MEDIUMBLOB, JSON




#################################################################################################################################################
# Order Relationships


class OrderRelations(db.Model):
    __tablename__ = 'order_relations'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    order_name = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    pick_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    pack_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    out_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL

    def __repr__(self):
        return f'<Out ID {self.out_id}>'


#################################################################################################################################################
# Shipping Results


class ShippingHistory(db.Model):
    __tablename__ = 'shipping_history'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    order_name = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    shipper = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    processed_at = db.Column(db.DateTime(timezone=True), nullable=True, default=func.now()) # DATETIME
    shipped_at = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
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
        return f'<Order Name {self.order_name}, Tracking Number {self.tracking_number}>'




class Labels(db.Model):
    __tablename__ = 'labels'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    order_name = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    tracking_number = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    label_id = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    zpl_data = db.Column(db.Text, nullable=False) # TEXT NOT NULL
    courier = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    method = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL

    def __repr__(self):
        return f'<Order Name {self.order_name}>'


#################################################################################################################################################
# General Data


class StateCodes(db.Model):
    __tablename__ = 'state_codes'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    region_name = db.Column(db.String(64), nullable=False) # VARCHAR(64) NOT NULL
    state_code = db.Column(db.String(4), nullable=False) # VARCHAR(4) NOT NULL

    def __repr__(self):
        return f'<Region {self.region_name}>'


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
    printer_loc = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    label_size = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    can_print_4x6 = db.Column(db.Boolean, nullable=False) # BOOLEAN NOT NULL
    can_print_4x675 = db.Column(db.Boolean, nullable=False) # BOOLEAN NOT NULL
    can_print = db.Column(JSON, nullable=False) # JSON NOT NULL

    def __repr__(self):
        return f'<Printer UNC \\{self.server_name}\{self.printer_name}>'