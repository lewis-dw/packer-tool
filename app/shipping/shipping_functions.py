def join_url(*url_parts):
    """
    Simple function to join all parts of the passed in url pieces and return
    This is because os.path.join doesnt work for URLs and i didnt want to muck about with other libraries when this is just as easy
    """
    url_parts = map(str, url_parts)
    full_url = '/'.join(url_parts).replace(' ', '%20')
    return full_url





def get_shipping_date(end_time, days_penalty, date_format):
    """
    
    """

    """
    pass in time in 24hr and days to add
    if its past that time then add days to todays date and return
    can even pass in a formatter
    """