from . import db
from datetime import datetime

class ShippedOrders(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    order_id = db.Column(db.String(100))
    name = db.Column(db.String(200))
    company = db.Column(db.String(200))
    postage_paid = db.Column(db.Float)
    shipping_cost = db.Column(db.Float)
    tracking_number = db.Column(db.String(100))
    status = db.Column(db.String(50))
    carrier = db.Column(db.String(50))
    service_type = db.Column(db.String(50))



class ShippingData:
    data = {
        "packaging_code": None,
        "shipping_service_code": None,
        "shipping_method": None,
        "shipping_address_line1": None,
        "shipping_address_line2": None,
        "shipping_address_line3": None,
        "shipping_address_statecode": None,
        "shipping_address_city": None,
        "shipping_address_postcode": None,
        "shipping_address_country": None,
        "shipping_company": None,
        "shipping_name": None,
        "shipping_tel": None,
        "shipping_email": None,
        "shipping_tax_eori": None,
        "shipping_order_id": None,
        "shipping_date": None,
        "shipping_cost": None,
        "package_dimensions": None,
        "invoice_items":{
            "Items": []
        }
    }