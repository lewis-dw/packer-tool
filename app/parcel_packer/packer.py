






def find_parcels(data):
    """
    Splits the order invoice lines into parcels for each individual items.
    For items that are over a certain volume threshold they are to be packed into their own individual parcel.
    """
    parcels = []
    final_parcels = []
    for line in data:
        for _ in range(int(float(line['product_demand_qty']))):
            # create item dict
            item_dict = {
                'unit_price': float(line['unit_price']),
                'unit_weight': float(line['unit_weight']),
                'unit_height': float(line['product_height']),
                'unit_width': float(line['product_width']),
                'unit_length': float(line['product_length']),
                'unit_volume': float(line['product_height']) * float(line['product_width']) * float(line['product_length'])
            }

            # based on volume of item decide which parcel list it goes into
            if item_dict['unit_volume'] > 50000:
                final_parcels.append(item_dict)
            else:
                parcels.append(item_dict)

    # sort the parcels by their volume
    parcels = sorted(
        parcels, 
        key=lambda x: x['unit_volume']
    )
    return parcels, final_parcels


def calculate_parcels(data):
    # first find the parcel lists (parcels is items we can put together, whereas final_parcels get their own parcel each)
    parcels, final_parcels = find_parcels(data)

    for parcel in parcels:
        # print(parcel)
        pass





def parse_form(form):
    """
    Loop over the form data and assign to a temp dict, this dict is then sorted by the key. (key is the index of each input)
    This is so that the indexes are sorted and flattened to [0, 1, 2...]. We do this because different browsers might scatter the parcel values. 
    """
    temp = {}
    for key, val in form.items():
        true_key, index = key.rsplit('_', 1)

        # add index to the temp dict
        if not temp.get(index, ''):
            temp[index] = {}
        temp[index][true_key] = float(val)

    # sort the keys ascending then take each value and assign it into parcels
    ordered_data = {key: temp[key] for key in sorted(temp.keys(), key=int)}
    parcels = [val for val in ordered_data.values()]
    return parcels




def temp_parcels():
    """This is temporary solution until we implement they actual parcel packager"""
    return [{
        'parcel_height': 4,
        'parcel_width': 2,
        'parcel_length': 2,
        'parcel_weight': 3,
        'parcel_quantity': 1,
        'parcel_insurance': 0
    }]