import datetime
import unittest
import os
import json

import pytz

import salvitobot
from salvitobot import config
from salvitobot import utils
from salvitobot.exceptions import NoCountryError


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.cwd = os.path.abspath(os.path.dirname(__file__))
        self.bot = salvitobot.Bot()

        with open(os.path.join(self.cwd, 'Quake', '1.json'), 'r') as handle:
            self.data1 = json.loads(handle.read())

    def test_parse_quake_data(self):
        result = utils.parse_quake_data(self.data1, 'Venezuela')

        expected = datetime.datetime(2015, 2, 5, 5, 38, 57, 769999, tzinfo=pytz.utc)
        self.assertEqual(1, len(result))
        self.assertEqual(expected, result[0]['datetime_utc'])

    def test_parse_quake_data_two_quakes(self):
        with open(os.path.join(self.cwd, 'Quake', '2.json'), 'r') as handle:
            data = json.loads(handle.read())

        result = utils.parse_quake_data(data, 'Venezuela')
        self.assertEqual(2, len(result))

    def test_get_quake(self):
        self.bot.get_quake(my_dict=self.data1, country='Venezuela')
        result = self.bot.quake
        expected = 1
        self.assertEqual(expected, len(result))

    def test_get_quake_strange_country(self):
        self.bot.get_quake(my_dict=self.data1, country='Vulcan')
        result = self.bot.quake
        expected = 0
        self.assertEqual(expected, len(result))

    def test_get_quake_from_web(self):
        self.bot.urls = [
            'http://pastebin.com/raw.php?i=0WuxsixK',
        ]
        self.bot.get_quake(country='Venezuela')
        result = self.bot.quake
        expected = 1
        self.assertEqual(expected, len(result))

    def test_get_quake_no_country(self):
        self.assertRaises(NoCountryError, self.bot.get_quake, self.data1)

    def test_is_new_quake(self):
        self.bot.get_quake(my_dict=self.data1, country='Venezuela')
        expected = True
        result = self.bot.is_new_quake()
        self.assertEqual(expected, result)

    def test_extract_nearby_cities(self):
        self.bot.get_quake(my_dict=self.data1, country='Venezuela')
        result = utils.extract_nearby_cities(self.bot.quake[0])
        expected = "a 2 km al SW de Umuquena, a 18 km al E de La Fria, a 31 km al NE de San Juan de Colon, y a 38 km al ESE de Puerto Santander, Colombia"
        self.assertEqual(expected, result)

    def test_create_db(self):
        utils.create_database(test=True)
        result = os.path.isfile(os.path.join(config.base_folder, "salvitobot_test.db"))
        self.assertTrue(result)

    def test_save_to_db(self):
        item = {
            'longitude': 126.3037,
            'time': 1423215548040,
            'latitude': 9.5166,
            'country': 'cortes',
            'place': '28km NNE de Cortes, Philippines',
            'tuit': 'SISMO. 4.8 grados mb en 28km NNE de Cortes, Philippines. A horas  http://earthquake.usgs.gov/earthquakes/eventpage/usc000tmn4',
            'type': 'earthquake',
            'magnitude_type': 'mb',
            'detail': 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/usc000tmn4.geojson',
            'link': 'http://earthquake.usgs.gov/earthquakes/eventpage/usc000tmn4',
            'code': 'c000tmn4',
            'depth': 84.37,
            'datetime_utc': datetime.datetime(2015, 2, 6, 9, 39, 8, 39999),
            'tz': 480,
            'magnitude': 4.8,
        }
        utils.save_to_db(item, test=True)

        db = utils.create_database(test=True)
        table = db['salvitobot']
        res = table.find_one(code='c000tmn4')
        self.assertIsNotNone(res)

        file = os.path.join(config.base_folder, "salvitobot_test.db")
        if os.path.isfile(file):
            os.remove(file)
