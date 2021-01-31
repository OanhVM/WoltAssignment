import json
import pathlib
from datetime import datetime

from flask import Flask, request, jsonify
from geopy.distance import geodesic
from werkzeug.exceptions import BadRequest

from restaurant import Restaurant

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

RESTAURANT_FILE_PATH = pathlib.Path().absolute().joinpath("src", "restaurants.json")
LATITUDE_NOT_FOUND_ERROR = "Latitude is required."
LATITUDE_FLOAT_VALIDATION_ERROR = "Latitude must be decimal degrees format and range from -90 to 90."
LONGITUDE_NOT_FOUND_ERROR = "Longitude is required."
LONGITUDE_FLOAT_VALIDATION_ERROR = "Longitude must be decimal degrees format and range from -180 to 180."
BLURHASH = "blurhash"
LAUNCH_DATE = "launch_date"
LOCATION = "location"
NAME = "name"
ONLINE = "online"
POPULARITY = "popularity"
RESTAURANTS = "restaurants"


def get_restaurants(customer_lat, customer_long):
    """
    Get information of Popular, New and Nearby Restaurants
    :param customer_lat: latitude of the given coordinate to discovery
    :param customer_long: longitude of the given coordinate to discovery
    :return: a json object include information of Popular Restaurants, New Restaurants and Nearby Restaurant
    """
    validate_customer_coordinates(customer_lat, customer_long)

    sections = []
    restaurants = get_close_restaurants(customer_lat, customer_long)

    popular_restaurants = get_popular_restaurants(restaurants)
    nearby_restaurants = get_nearby_restaurants(restaurants)
    new_restaurants = get_new_restaurants(restaurants)

    if popular_restaurants is not None:
        sections.append(build_response("Popular Restaurants", popular_restaurants))
    if new_restaurants is not None:
        sections.append(build_response("New Restaurants", new_restaurants))
    if nearby_restaurants is not None:
        sections.append(build_response("Nearby Restaurants", nearby_restaurants))

    return {"sections": sections}


def build_response(title, restaurants):
    """
    Build json object response for each restaurants section
    :param title:
    :param restaurants:
    :return:
    """
    return {
        "title": title,
        "restaurants": [ob.as_response_dict() for ob in restaurants]
    }


def get_data_from_json_file():
    """
    Get all restaurants in json file
    :return:
    """
    with open(RESTAURANT_FILE_PATH) as json_file:
        return json.load(json_file)["restaurants"]


def get_available_restaurants():
    """
    Convert json object to Restaurants objects
    :return: list Restaurant objects
    """
    restaurants = []
    restaurants_data = get_data_from_json_file()
    for restaurant_json in restaurants_data:
        restaurant = Restaurant(
            blurhash=restaurant_json[BLURHASH],
            launch_date=restaurant_json[LAUNCH_DATE],
            location=restaurant_json[LOCATION],
            name=restaurant_json[NAME],
            online=restaurant_json[ONLINE],
            popularity=restaurant_json[POPULARITY])

        restaurant.launched_days = get_launched_days(restaurant.launch_date)

        restaurants.append(restaurant)

    return restaurants


def get_close_restaurants(customer_lat, customer_long):
    """
    Get restaurant closer than 1.5 kilometers from customer coordinates
    :return:
    """
    restaurants = get_available_restaurants()

    close_restaurants = []

    for restaurant in restaurants:
        restaurant.distance = geodesic((customer_lat, customer_long), restaurant.location).km

        if restaurant.distance <= 1.5:
            close_restaurants.append(restaurant)

    return close_restaurants


def get_popular_restaurants(restaurants, cutoff=10):
    """
    Get top 10 popular restaurants
    :param restaurants:
    :param cutoff:
    :return:
    """
    restaurants = sorted(restaurants, key=lambda x: (-x.online, -float(x.popularity)))[:cutoff]
    if len(restaurants) == 0:
        return None
    else:
        return restaurants


def get_nearby_restaurants(restaurants, cutoff=10):
    """
    Get top 10 nearby restaurants
    :param cutoff:
    :param restaurants:
    :return:
    """
    restaurants = sorted(restaurants, key=lambda x: (-x.online, float(x.distance)))[:cutoff]
    if len(restaurants) == 0:
        return None
    else:
        return restaurants


def get_new_restaurants(restaurants, cutoff=10):
    """
    Get top 10 new restaurants
    :param cutoff:
    :param restaurants:
    :return:
    """
    restaurants = [res for res in restaurants if res.launched_days <= 120]
    restaurants = sorted(restaurants, key=lambda x: (-x.online, float(x.launched_days)))[:cutoff]
    if len(restaurants) == 0:
        return None
    else:
        return restaurants


def get_launched_days(launch_date):
    """
    Get number of days which restaurants joined Wolt
    :param launch_date:
    :return:
    """
    return (datetime.today() - datetime.strptime(launch_date, "%Y-%m-%d")).days


def validate_latitude(customer_lat):
    """
    Validate customer's latitude
    :param customer_lat:
    :return:
    """
    if not customer_lat:
        raise BadRequest(LATITUDE_NOT_FOUND_ERROR)
    else:
        try:
            customer_lat = float(customer_lat)
            if not -90 <= customer_lat <= 90:
                raise BadRequest(LATITUDE_FLOAT_VALIDATION_ERROR)
        except ValueError:
            raise BadRequest(LATITUDE_FLOAT_VALIDATION_ERROR)


def validate_longitude(customer_long):
    """
    Validate customer's longitude
    :param customer_long:
    :return:
    """
    if not customer_long:
        raise BadRequest(LONGITUDE_NOT_FOUND_ERROR)
    else:
        try:
            customer_long = float(customer_long)
            if not -180 <= customer_long <= 180:
                raise BadRequest(LONGITUDE_FLOAT_VALIDATION_ERROR)
        except ValueError:
            raise BadRequest(LONGITUDE_FLOAT_VALIDATION_ERROR)


def validate_customer_coordinates(customer_lat, customer_long):
    """
    Validate customer coordinates
    :param customer_lat: customer's latitude
    :param customer_long: customer's longitude
    :return:
    """
    validate_latitude(customer_lat)
    validate_longitude(customer_long)


@app.route("/discovery", methods=["GET"])
def discovery():
    customer_lat = request.args.get("lat")
    customer_long = request.args.get("lon")

    return jsonify(get_restaurants(customer_lat, customer_long))


if __name__ == '__main__':
    app.run()
    # get_available_restaurants()

    # print(json.dumps(get_restaurants(24.941244, 60.174), indent=4))
