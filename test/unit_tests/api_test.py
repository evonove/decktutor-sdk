import unittest
import datetime
from mock import Mock, patch
from decktutorsdk import decktutor
from decktutorsdk.api import api_factory
from decktutorsdk.exceptions import ResourceNotFound, MissingConfig


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.username = "test"
        self.password = "password"
        self.api = decktutor.Api(
            username=self.username, password=self.password, authenticate=True
        )
        self.api.request = Mock()
        self.order_attributes = {
            "date": "01-01-2015",
            "number": "4417119669820331",
            "item_id": "11",
            "first_name": "Joy",
            "last_name": "Deck"
        }
        self.auth_token = "test_auth_token"
        self.auth_token_secret = "test_auth_token_secret"
        self.api_factory = api_factory

    def test_default_config(self):

        with self.assertRaises(MissingConfig):
            self.api_factory.get()
        self.api_factory.configure(username=self.username, password=self.password)
        api = self.api_factory.get(authenticate=True)
        self.assertEqual(api.password, self.password)
        self.assertEqual(api.username, self.username)
        self.assertTrue(api.authenticate)
        api.token = self.auth_token
        #the configuration is lazy loaded, this api instance is not authenticated so it loads the new config
        self.api_factory.configure(username="another_username", password="another_password", )
        api = self.api_factory.get(authenticate=False)
        self.assertEqual(api.password, "another_password")
        self.assertEqual(api.username, "another_username")
        self.assertTrue(not api.authenticate)
        self.assertNotEqual(api.token, self.auth_token)

    def test_endpoint(self):
        new_api = decktutor.Api(mode="live", username="dummy", password="dummy")
        self.assertEqual(new_api.endpoint, "http://dev.decktutor.com/ws-2.0/app/v2")
        self.assertEqual(new_api.token_endpoint, "http://dev.decktutor.com/ws-2.0/app/v2/account/login")

        new_api = decktutor.Api(mode="sandbox", username="dummy", password="dummy")
        self.assertEqual(new_api.endpoint, "http://dev.decktutor.com/ws-2.0/app/v2")
        self.assertEqual(new_api.token_endpoint, "http://dev.decktutor.com/ws-2.0/app/v2/account/login")

        new_api = decktutor.Api(endpoint="https://custom-endpoint.decktutor.com", username="dummy", password="dummy")
        self.assertEqual(new_api.endpoint, "https://custom-endpoint.decktutor.com")
        self.assertEqual(new_api.token_endpoint, "https://custom-endpoint.decktutor.com/account/login")

    def test_authenticate(self):
        new_api = decktutor.Api(username="dummy", password="dummy")
        self.assertEqual(new_api.authenticate, False)

        new_api = decktutor.Api(username="dummy", password="dummy", authenticate=True)
        self.assertEqual(new_api.authenticate, True)

    def test_get(self):
        payment_history = self.api.request("/payments/payment?cnt=1", "GET")
        self.api.request.assert_called_once_with('/payments/payment?cnt=1', 'GET')

    def test_post(self):
        self.api.request.return_value = {'id': 'test'}
        order = self.api.request("/create/order", "POST", self.order_attributes)

        self.assertEqual(order.get('error'), None)
        self.assertEqual(order.get('id'), 'test')

    def test_bad_request(self):
        self.api.request.return_value = {'error': 'test'}
        order = self.api.request("/create/order", "POST", {})

        self.api.request.assert_called_once_with("/create/order",
                                                 'POST',
                                                 {})
        self.assertNotEqual(order.get('error'), None)

    @patch('decktutorsdk.api.Api.http_call', autospec=True)
    def test_expired_time(self, mock_http_call):
        token = {
            "auth_token": "test",
            "auth_token_expiration": str(datetime.datetime.now() - datetime.timedelta(days=1)),
            "auth_token_secret": "test"
        }
        self.api.token = token
        new_token = self.api.get_token()
        self.assertNotEqual(token, new_token)

    @patch('decktutorsdk.api.Api.http_call', autospec=True)
    def test_incremental_increments(self, mock_req):
        old_incr = self.api.incremental
        self.api.headers()
        new_incr = self.api.incremental
        self.assertNotEqual(old_incr, new_incr)
        #is incremented by +1
        self.assertEqual(new_incr, old_incr+1)

    def test_not_found(self):
        self.api.request.side_effect = ResourceNotFound("error")
        self.assertRaises(ResourceNotFound, self.api.request, ("/payments/payment?cnt=1", "GET"))

    @patch('decktutorsdk.api.Api.http_call', autospec=True)
    def test_get_auth_token(self, mock_http):
        mock_http.return_value = {
            'auth_token': self.auth_token,
            'auth_token_expiration': '2014-12-31T11:09:45+00:00',
            'auth_token_secret': self.auth_token_secret,
        }
        auth_token = self.api.get_token()['auth_token']
        mock_http.assert_called_once_with(self.api,
                                          'http://dev.decktutor.com/ws-2.0/app/v2/account/login', 'POST',
                                          data='{"login":"%s", "password":"%s"}' % (self.username, self.password),
                                          headers={
                                              "Content-Type": "application/json",
                                              "Accept": "application/json",
                                              "User-Agent": self.api.user_agent
                                          })
        self.assertEqual(auth_token, self.auth_token)

    @patch('decktutorsdk.decktutor.Api.http_call', autospec=True)
    def test_get_auth_secret_token(self, mock_http):
        mock_http.return_value = {
            'auth_token': self.auth_token,
            'auth_token_expiration': '2014-12-31T11:09:45+00:00',
            'auth_token_secret': self.auth_token_secret,
        }
        auth_token_secret = self.api.get_token()['auth_token_secret']
        mock_http.assert_called_once_with(self.api,
                                          'http://dev.decktutor.com/ws-2.0/app/v2/account/login', 'POST',
                                          data='{"login":"%s", "password":"%s"}' % (self.username, self.password),
                                          headers={
                                              "Content-Type": "application/json",
                                              "Accept": "application/json",
                                              "User-Agent": self.api.user_agent
                                          })
        self.assertEqual(auth_token_secret, self.auth_token_secret)