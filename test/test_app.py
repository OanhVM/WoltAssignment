import unittest

from mockito import when, mock
from werkzeug.exceptions import BadRequest

import app
from app import validate_latitude, LATITUDE_NOT_FOUND_ERROR, LATITUDE_FLOAT_VALIDATION_ERROR, \
    LONGITUDE_FLOAT_VALIDATION_ERROR, validate_longitude, LONGITUDE_NOT_FOUND_ERROR, get_close_restaurants, \
    get_popular_restaurants, get_nearby_restaurants, get_new_restaurants, get_restaurants
from restaurant import Restaurant


class TestSum(unittest.TestCase):

    def test_validate_latitude(self):
        with self.subTest(f"BadRequest {LATITUDE_NOT_FOUND_ERROR}"):
            with self.assertRaises(BadRequest) as err_cm:
                validate_latitude("")
            self.assertTrue(LATITUDE_NOT_FOUND_ERROR in str(err_cm.exception))

        with self.subTest(f"BadRequest {LATITUDE_NOT_FOUND_ERROR}: not float"):
            with self.assertRaises(BadRequest) as err_cm:
                validate_latitude("abc.")
            self.assertTrue(LATITUDE_FLOAT_VALIDATION_ERROR in str(err_cm.exception))

        with self.subTest(f"BadRequest {LATITUDE_NOT_FOUND_ERROR}: out of range"):
            with self.assertRaises(BadRequest) as err_cm:
                validate_latitude("100")
            self.assertTrue(LATITUDE_FLOAT_VALIDATION_ERROR in str(err_cm.exception))

            with self.assertRaises(BadRequest) as err_cm:
                validate_latitude("-100")
            self.assertTrue(LATITUDE_FLOAT_VALIDATION_ERROR in str(err_cm.exception))

    def test_validate_longitude(self):
        with self.subTest(f"BadRequest {LONGITUDE_NOT_FOUND_ERROR}"):
            with self.assertRaises(BadRequest) as err_cm:
                validate_longitude("")
            self.assertTrue(LONGITUDE_NOT_FOUND_ERROR in str(err_cm.exception))

        with self.subTest(f"BadRequest {LONGITUDE_FLOAT_VALIDATION_ERROR}: not float"):
            with self.assertRaises(BadRequest) as err_cm:
                validate_longitude("abc.")
            self.assertTrue(LONGITUDE_FLOAT_VALIDATION_ERROR in str(err_cm.exception))

        with self.subTest(f"BadRequest {LONGITUDE_FLOAT_VALIDATION_ERROR}: out of range"):
            with self.assertRaises(BadRequest) as err_cm:
                validate_longitude("200")
            self.assertTrue(LONGITUDE_FLOAT_VALIDATION_ERROR in str(err_cm.exception))

            with self.assertRaises(BadRequest) as err_cm:
                validate_longitude("-300")
            self.assertTrue(LONGITUDE_FLOAT_VALIDATION_ERROR in str(err_cm.exception))

    def test_get_close_restaurants(self):
        mock_near_restaurant_1 = mock({"location": [24.936465, 60.178633]}, spec=Restaurant)
        mock_near_restaurant_2 = mock({"location": [24.936, 60.1783]}, spec=Restaurant)
        mock_far_restaurant_1 = mock({"location": [24.2, 60.2]}, spec=Restaurant)

        mock_restaurants = [mock_near_restaurant_1, mock_near_restaurant_2, mock_far_restaurant_1]
        when(app).get_available_restaurants().thenReturn(mock_restaurants)

        close_restaurants = get_close_restaurants(24.941244, 60.174)

        self.assertEqual(close_restaurants, [mock_near_restaurant_1, mock_near_restaurant_2])

    def test_get_popular_restaurants(self):
        with self.subTest("Popular descending order"):
            mock_popular_restaurant_1 = mock({"online": False, "popularity": 0.1}, spec=Restaurant)
            mock_popular_restaurant_2 = mock({"online": False, "popularity": 0.2}, spec=Restaurant)
            mock_popular_restaurant_3 = mock({"online": True, "popularity": 0.3}, spec=Restaurant)
            mock_popular_restaurant_4 = mock({"online": True, "popularity": 0.4}, spec=Restaurant)

            moc_restaurants = [mock_popular_restaurant_1, mock_popular_restaurant_2, mock_popular_restaurant_3,
                               mock_popular_restaurant_4]
            popular_restaurants = get_popular_restaurants(moc_restaurants, cutoff=3)
            self.assertEqual(popular_restaurants,
                             [mock_popular_restaurant_4, mock_popular_restaurant_3,
                              mock_popular_restaurant_2])

        with self.subTest("None list"):
            restaurants = []
            self.assertEqual(None, get_popular_restaurants(restaurants))

    def test_get_nearby_restaurants(self):
        with self.subTest("Nearby ascending order"):
            mock_popular_restaurant_1 = mock({"online": False, "distance": 0.1}, spec=Restaurant)
            mock_popular_restaurant_2 = mock({"online": False, "distance": 0.2}, spec=Restaurant)
            mock_popular_restaurant_3 = mock({"online": True, "distance": 0.3}, spec=Restaurant)
            mock_popular_restaurant_4 = mock({"online": True, "distance": 0.4}, spec=Restaurant)

            moc_restaurants = [mock_popular_restaurant_1, mock_popular_restaurant_2, mock_popular_restaurant_3,
                               mock_popular_restaurant_4]
            popular_restaurants = get_nearby_restaurants(moc_restaurants, cutoff=3)
            self.assertEqual(popular_restaurants,
                             [mock_popular_restaurant_3, mock_popular_restaurant_4,
                              mock_popular_restaurant_1])

        with self.subTest("None list"):
            restaurants = []
            self.assertEqual(None, get_nearby_restaurants(restaurants))

    def test_get_new_restaurants(self):
        with self.subTest("New Restaurants descending order"):
            mock_popular_restaurant_1 = mock({"online": False, "launched_days": 10}, spec=Restaurant)
            mock_popular_restaurant_2 = mock({"online": False, "launched_days": 20}, spec=Restaurant)
            mock_popular_restaurant_3 = mock({"online": True, "launched_days": 30}, spec=Restaurant)
            mock_popular_restaurant_4 = mock({"online": True, "launched_days": 40}, spec=Restaurant)
            mock_popular_restaurant_5 = mock({"online": True, "launched_days": 160}, spec=Restaurant)

            moc_restaurants = [mock_popular_restaurant_1, mock_popular_restaurant_2, mock_popular_restaurant_3,
                               mock_popular_restaurant_4, mock_popular_restaurant_5]
            popular_restaurants = get_new_restaurants(moc_restaurants, cutoff=3)
            self.assertEqual(popular_restaurants,
                             [mock_popular_restaurant_3, mock_popular_restaurant_4,
                              mock_popular_restaurant_1])

        with self.subTest("None list"):
            restaurants = []
            self.assertEqual(None, get_new_restaurants(restaurants))

    def test_get_restaurants(self):
        customer_lat, customer_long = 10, 20
        mock_data_popular = {
            "title": "Popular Restaurants",
            "restaurants": "Test"
        }
        mock_data_new = {
            "title": "New Restaurants",
            "restaurants": "Test"
        }
        mock_data_nearby = {
            "title": "Nearby Restaurants",
            "restaurants": "Test"
        }
        when(app).validate_customer_coordinates(customer_lat, customer_long).thenReturn("")
        when(app).get_close_restaurants(customer_lat, customer_long).thenReturn("")

        when(app).get_popular_restaurants("").thenReturn([])
        when(app).build_response("Popular Restaurants", []).thenReturn(mock_data_popular)

        when(app).get_new_restaurants("").thenReturn([])
        when(app).build_response("New Restaurants", []).thenReturn(mock_data_new)

        when(app).get_nearby_restaurants("").thenReturn([])
        when(app).build_response("Nearby Restaurants", []).thenReturn(mock_data_nearby)

        self.assertEqual({"sections": [mock_data_popular, mock_data_new, mock_data_nearby]},
                         get_restaurants(customer_lat, customer_long))


if __name__ == '__main__':
    unittest.main()
