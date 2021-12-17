import configparser
import requests

def google_find_place(input_text):
    # read values from ini
    config = configparser.ConfigParser()
    config.read('token.ini')
    google_map_key = config.get('token','google_map_key')

    # google maps
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'

    params = dict(
        input=input_text,
        inputtype='textquery',
        fields='photos,formatted_address,name,rating,opening_hours,geometry',
        key=google_map_key
    )

    resp = requests.get(url=url, params=params)
    data = resp.json()

    return data
