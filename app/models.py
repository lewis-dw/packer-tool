from app import db
from sqlalchemy.sql import func



class ShippingHistory(db.Model):
    __tablename__ = 'shipping_history'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    order_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    date_shipped = db.Column(db.DateTime(timezone=True), nullable=True, default=func.now()) # DATETIME
    name = db.Column(db.String(64), nullable=False) # VARCHAR(64) NOT NULL
    company = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL
    customer_paid = db.Column(db.Numeric(10, 2), nullable=False) # NUMERIC(10, 2) NOT NULL
    dw_paid = db.Column(db.Numeric(10, 2), nullable=False) # NUMERIC(10, 2) NOT NULL
    tracking_number = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    courier = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    method = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL

    def __repr__(self):
        return f'<Order {self.order_id}>'



class Orders(db.Model):
    __tablename__ = 'test_orders'
    id = db.Column(db.Integer, primary_key=True) # INTEGER NOT NULL AUTO_INCREMENT
    order_id = db.Column(db.String(16), nullable=False) # VARCHAR(16) NOT NULL
    date_shipped = db.Column(db.DateTime(timezone=True), nullable=True, default=func.now()) # DATETIME
    name = db.Column(db.String(64), nullable=False) # VARCHAR(64) NOT NULL
    company = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL
    customer_paid = db.Column(db.Numeric(10, 2), nullable=False) # NUMERIC(10, 2) NOT NULL
    dw_paid = db.Column(db.Numeric(10, 2), nullable=False) # NUMERIC(10, 2) NOT NULL
    tracking_number = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    courier = db.Column(db.String(32), nullable=False) # VARCHAR(32) NOT NULL
    method = db.Column(db.String(80), nullable=False) # VARCHAR(80) NOT NULL

    def __repr__(self):
        return f'<Order {self.order_id}>'