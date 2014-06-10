import unittest
from decktutorsdk.api import Api
from decktutorsdk.decktutor import decktutor, set_default_config, set_auth_config


class Decktutor(unittest.TestCase):

    def setUp(self):
        self.username = "test"
        self.password = "password"
        self.api = Api(
            username=self.username, password=self.password, authenticate=True
        )

    def test_good_resolver(self):

        item = decktutor.insertions.info(url_entry={'code': 123})