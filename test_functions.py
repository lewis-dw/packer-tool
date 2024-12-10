from app.shipper import ups, fedex

url = ''

payload = {}

res = fedex.send_payload(url, payload)

print(res.json())