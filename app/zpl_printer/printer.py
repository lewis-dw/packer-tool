import socket
import json





def send_zpl_to_server(server_name, printer_name, zpl_data):
    try:
        # Prepare the JSON payload
        payload = {
            "printer": printer_name,
            "zpl_data": zpl_data
        }

        # Connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            port=9100 # this will always be this
            s.connect((server_name, port))
            s.sendall(json.dumps(payload).encode())
    except Exception as e:
        print(f"Error: {e}")





zpl_data=[
    '^XA',
    '^FO50,50',
    '^A0N,50,50^FDHello, World!^FS',
    '^XZ'
]

send_zpl_to_server(
    'LOGISTICS',
    'wifizebra',
    ''.join(zpl_data)
)


"""
Add to db
server_name     printer_name    can_print_4x6   can_print_4x675
LOGISTICS       UPS             True            False
LOGISTICS       Fedex           True            True
LOGISTICS       wifizebra       True            False
LOGISTICS       Royal Mail      True            False
"""