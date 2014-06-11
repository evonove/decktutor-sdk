import unittest
from decktutorsdk.api import api_factory
from decktutorsdk.decktutor import decktutor


class SearchTest(unittest.TestCase):
    def setUp(self):
        self.username = "evonove"
        self.password = "evonove"
        self.api_factory = api_factory
        self.api_factory.configure(username=self.username, password=self.password)

    def test_card_version(self):
        item = decktutor.search.card_version(params={'game': 'mtg', 'name': 'Phyrexian Negator', 'set': 'UDS'})
        token = self.api_factory.get().token
        token_time = self.api_factory.get().token_request_at
        item = decktutor.search.card_version(params={'game': 'mtg', 'name': 'Phyrexian Negator', 'set': 'UDS'})
        new_token = self.api_factory.get().token
        new_token_time = self.api_factory.get().token_request_at
        self.assertEqual(token, new_token)
        self.assertEqual(token_time, new_token_time)
        print item