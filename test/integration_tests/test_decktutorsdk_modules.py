
import json
import unittest
from mock import patch
from decktutorsdk.api import api_factory
from decktutorsdk.decktutor import decktutor


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.username = "test"
        self.password = "password"
        self.api_factory = api_factory
        self.api_factory.configure(username=self.username, password=self.password)

    @patch('decktutorsdk.api.Api.http_call', autospec=True)
    def test_account_login(self, mock_response):
        auth_token = "5T23GENtqCAPbIQZnSIdLulyqSCRAyefl/nTKGLgLzBLaZKz2msjsw=="
        nick = "Joy"
        auth_token_expiration = "2014-05-22T07:36:42+00:00"
        auth_token_secret = "a7f0b0974d236c88e27b7e27ca08796c69d9c5ee"
        login_response = """{
            "auth_token": "%s",
            "auth_token_expiration": "%s",
            "auth_token_secret": "%s",
            "user": {
                "level": 1,
                "timestamp": "2014-05-08T14:21:03+02:00",
                "nick": "%s",
                "motd": "",
                "avatar_large": null,
                "avatar_small": null,
                "in_vacation": false,
                "feedback": 0,
                "feedbackpercent": null,
                "feedbacktrend": null
            }
        }""" % (auth_token, auth_token_expiration, auth_token_secret, nick)

        mock_response.return_value = json.loads(login_response)
        item = decktutor.account.login(body='{"login":"%s", "password":"%s"}' % (self.username, self.password))
        self.assertEqual(item.get('auth_token'), auth_token)
        self.assertEqual(item.get('auth_token_secret'), auth_token_secret)
        self.assertEqual(item.get('auth_token_expiration'), auth_token_expiration)
        self.assertEqual(item.get('user').get('nick'), nick)
