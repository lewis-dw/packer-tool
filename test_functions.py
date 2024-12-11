from app.shipper import ups, fedex
from app.odoo.api import send_message

# url = ''
# payload = {}
# res = fedex.send_payload(url, payload)
# print(res.json())


send_message('1', 'UPS', '123')