from app import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import MEDIUMBLOB, MEDIUMTEXT, JSON
from sqlalchemy import and_

# this is for an error message return for printers
from app.print_zpl import printer




#################################################################################################################################################
# Order Relationships


"""
UNUSED - Order relationship between order name and the pick, pack, and out IDs
"""
class OrderRelations(db.Model):
    __tablename__ = 'order_relations'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    order_name = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    pick_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    pack_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    out_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL

    def __repr__(self):
        return f'<Out ID {self.out_id}>'

    @staticmethod
    def add_row(order_name, pick_id, pack_id, out_id):
        db.session.add(OrderRelations(
            order_name=order_name,
            pick_id=pick_id,
            pack_id=pack_id,
            out_id=out_id
        ))
        db.session.commit()



#################################################################################################################################################
# Shipping Results


"""
History of everything ever shipped with all the relevant details about those orders
"""
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

    @staticmethod
    def add_row(order_name, shipper, processed_at, shipped_at, name, company, shipped_to, customer_paid, dw_paid, tracking_number, courier, method, commercial_invoice):
        db.session.add(ShippingHistory(
            order_name=order_name,
            shipper=shipper,
            processed_at=processed_at,
            shipped_at=shipped_at,
            name=name,
            company=company,
            shipped_to=shipped_to,
            customer_paid=customer_paid,
            dw_paid=dw_paid,
            tracking_number=tracking_number,
            courier=courier,
            method=method,
            commercial_invoice=commercial_invoice
        ))
        db.session.commit()

    @staticmethod
    def search_for_invoice(order_id):
        """
        get all available commercial invoices for the order_id passed
        """

        # query the table
        results = db.session.query(ShippingHistory).filter(
            ShippingHistory.order_name == order_id,
            ShippingHistory.commercial_invoice != None
        ).all()

        if results:
            return {'state': 'Success', 'value': results}
        else:
            return {'state': 'Error', 'value': f'No commercial invoices found for order name: {order_id}'}

    @staticmethod
    def search_row_id(row_id):
        order_name, commercial_invoice = db.session.query(ShippingHistory.order_name, ShippingHistory.commercial_invoice).filter(
            ShippingHistory.id == row_id
        ).first()

        # we dont need to validate that there is data there because this is a direct row get from a prior query so it should be there
        return order_name, commercial_invoice



"""
All labels ever created for all shipped orders
"""
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

    @staticmethod
    def add_row(order_name, tracking_number, label_id, zpl_data, courier, method):
        db.session.add(Labels(
            order_name=order_name,
            tracking_number=tracking_number,
            label_id=label_id,
            zpl_data=zpl_data,
            courier=courier,
            method=method
        ))
        db.session.commit()

    @staticmethod
    def get_zpl_data(label_id):
        zpl_data = db.session.query(Labels.zpl_data).filter(
            Labels.label_id == label_id
        ).scalar() # returns first item of the result - in this case the zpl_data

        # we dont need to validate that there is data there because this label id is from a prior query so it should exist
        return zpl_data

    @staticmethod
    def get_labels_for_order(order_id):
        """
        get all labels related to the order_id passed
        """

        # query the table
        results = db.session.query(Labels).filter(
            Labels.order_name == order_id
        ).all()

        # parse the results
        if results:
            return {'state': 'Success', 'value': results}
        else:
            return {'state': 'Error', 'value': f'No labels found for order name: {order_id}'}


#################################################################################################################################################
# Shipping Data


"""
State Codes for USA, Canada, and Ireland
"""
class StateCodes(db.Model):
    __tablename__ = 'state_codes'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    region_name = db.Column(db.String(64), nullable=False) # VARCHAR(64) NOT NULL
    state_code = db.Column(db.String(4), nullable=False) # VARCHAR(4) NOT NULL

    def __repr__(self):
        return f'<Region {self.region_name}>'

    @staticmethod
    def add_row(region_name, state_code):
        db.session.add(StateCodes(
            region_name=region_name,
            state_code=state_code
        ))
        db.session.commit()

    @staticmethod
    def get_state_code(region_name):
        """
        Returns the statecode for a given region
        """

        # query the table
        state_code = db.session.query(StateCodes.state_code).filter(
            StateCodes.region_name == str(region_name).upper()
        ).scalar() # returns first item of the result - in this case the state_code
        return state_code



"""
Countries with data like the shipping country code, if they accept ETD and if they accept saturday deliveries
"""
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

    @staticmethod
    def add_row(country_name, country_code, shipping_country_code, etd_required, sat_indicator):
        db.session.add(Countries(
            country_name=country_name,
            country_code=country_code,
            shipping_country_code=shipping_country_code,
            etd_required=etd_required,
            sat_indicator=sat_indicator
        ))
        db.session.commit()

    @staticmethod
    def get_country_data(country_name):
        country_data = db.session.query(Countries).filter(
            Countries.country_name == country_name
        ).first()
        return country_data

    @staticmethod
    def get_all_country_codes():
        """
        Returns all country names to shipping country code as a dictionary
        """

        # query the table
        results = db.session.query(Countries.country_name, Countries.shipping_country_code).all()
        country_dict = {country_id: country_name for country_name, country_id in results}
        return country_dict

    @staticmethod
    def get_country_code(country):
        """
        Returns the country code for a given country for the invoice items
        """

        # query the table
        country_code = db.session.query(Countries.shipping_country_code).filter(
            Countries.country_name == country
        ).scalar() # returns first item of the result - in this case the shipping_country_code

        if country_code:
            return country_code
        else:
            return 'Can\'t find country code'



"""
Country codes against their respective flag in SVG form
"""
class CountryFlags(db.Model):
    __tablename__ = 'shipping_flags'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    country_code = db.Column(db.String(4), nullable=False) # VARCHAR(4) NOT NULL
    flag_svg = db.Column(MEDIUMTEXT, nullable=False)  # TEXT NOT NULL

    def __repr__(self):
        return f'<Country ID {self.country_code}>'

    @staticmethod
    def add_row(country_code, flag_svg):
        db.session.add(CountryFlags(
            country_code=country_code,
            flag_svg=flag_svg
        ))
        db.session.commit()

    @staticmethod
    def get_flag_svg(country_id):
        """
        Returns the country code for a given country for the invoice items
        """

        # query the table
        svg_data = db.session.query(CountryFlags.flag_svg).filter(
            CountryFlags.country_code == country_id
        ).scalar() # returns first item of the result - in this case the flag_svg

        if svg_data:
            return svg_data
        else:
            return 'N/A'


#################################################################################################################################################
# Backend Data


"""
Technical shipping code against the friendly human readable version
"""
class ShippingCodes(db.Model):
    __tablename__ = 'shipping_codes'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    shipping_code = db.Column(db.String(128), nullable=False) # VARCHAR(128) NOT NULL
    friendly_code = db.Column(db.String(128), nullable=False) # VARCHAR(128) NOT NULL

    def __repr__(self):
        return f'<Shipping Code {self.friendly_code}>'

    @staticmethod
    def add_row(shipping_code, friendly_code):
        db.session.add(ShippingCodes(
            shipping_code=shipping_code,
            friendly_code=friendly_code
        ))
        db.session.commit()

    @staticmethod
    def get_friendly_code(shipping_code, sat_indicator):
        friendly_code = db.session.query(ShippingCodes.friendly_code).filter(
            ShippingCodes.shipping_code == f'{shipping_code}{sat_indicator}'
        ).scalar() # returns first item of the result - in this case the friendly_code

        if friendly_code is not None: # match
            return friendly_code
        else: # no match
            return shipping_code



"""
Printer info like what printers we have online, what they can print and where they are
"""
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

    @staticmethod
    def add_row(server_name, printer_name, printer_loc, label_size, can_print_4x6, can_print_4x675, can_print):
        db.session.add(Printers(
            server_name=server_name,
            printer_name=printer_name,
            printer_loc=printer_loc,
            label_size=label_size,
            can_print_4x6=can_print_4x6,
            can_print_4x675=can_print_4x675,
            can_print=can_print
        ))
        db.session.commit()

    @staticmethod
    def find_printer(printer_loc, courier):
        # query the table for results and grab the first row that satisfies these conditions
        result = db.session.query(Printers).filter(
            and_(
                Printers.printer_loc == printer_loc,
                Printers.can_print.contains(courier.lower())
            )
        ).order_by(Printers.can_print_4x675.desc()).first() # order by if it can print 4x6.75 or not and grab first

        # parse the result
        if result:
            return {'state': 'Success', 'value': (result.server_name, result.printer_name, result.label_size)}
        else:
            return {'state': 'Error', 'value': f'No printer could be found that can print {courier} in {printer.friendly_translate(printer_loc)}'}



"""
Replacement table for text in product descriptions
"""
class ProductOptions(db.Model):
    __tablename__ = 'product_options'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    find_this = db.Column(db.Text, nullable=False) # TEXT NOT NULL
    replace_with = db.Column(db.String(64), nullable=False) # VARCHAR(64) NOT NULL

    def __repr__(self):
        return f'<Replace {self.find_this} -> {self.replace_with}>'

    @staticmethod
    def add_row(find_this, replace_with):
        db.session.add(ProductOptions(
            find_this=find_this,
            replace_with=replace_with
        ))
        db.session.commit()
    
    @staticmethod
    def get_replacers():
        description_translate = db.session.query(ProductOptions.find_this, ProductOptions.replace_with).all()
        return description_translate
