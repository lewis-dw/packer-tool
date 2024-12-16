possible_boxes = [
    {
        'name': 'Large Box',
        'H': 6.0,
        'W': 6.0,
        'L': 6.0
    },
    {
        'name': 'Medium Box',
        'H': 4.0,
        'W': 4.0,
        'L': 4.0
    },
    {
        'name': 'Small Box',
        'H': 2.0,
        'W': 2.0,
        'L': 2.0
    }
]


parcels = [
    {
        'unit_price': 1.0,
        'unit_weight': 1.0,
        'unit_height': 2.0,
        'unit_width': 2.0,
        'unit_length': 2.0,
        'unit_volume': 8.0,
    },
    {
        'unit_price': 2.0,
        'unit_weight': 2.0,
        'unit_height': 3.0,
        'unit_width': 2.0,
        'unit_length': 2.0,
        'unit_volume': 12.0,
    }
]

parcels = sorted(
    parcels, 
    key=lambda x: x['unit_volume']
)


################################
# Code for parcel packing here: