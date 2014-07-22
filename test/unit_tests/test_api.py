import unittest
from ..test_helper import mock
from decktutorsdk.api import Api, ApiFactory
from decktutorsdk.exceptions import ResourceNotFound, MissingConfig


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.username = "test"
        self.password = "password"
        self.endpoint = "http://dev.decktutor.com/ws-2.0/app/v2"
        self.api = Api(
            username=self.username, password=self.password, authenticate=True
        )
        self.api.request = mock.Mock()
        self.order_attributes = {
            "date": "01-01-2015",
            "number": "4417119669820331",
            "item_id": "11",
            "first_name": "Joy",
            "last_name": "Leggero"
        }
        self.auth_token = "test_auth_token"
        self.auth_token_secret = "test_auth_token_secret"
        self.api_factory = ApiFactory()

    def test_default_config(self):

        with self.assertRaises(MissingConfig):
            self.api_factory.get_instance()
        self.api_factory.configure(username=self.username, password=self.password)
        api = self.api_factory.get_instance(authenticate=True)
        self.assertEqual(api.password, self.password)
        self.assertEqual(api.username, self.username)
        self.assertTrue(api.authenticate)
        api.token = self.auth_token
        #the configuration is lazy loaded, this api instance is not authenticated so it loads the new config
        self.api_factory.configure(username="another_username", password="another_password")
        api = self.api_factory.get_instance(authenticate=False)
        self.assertEqual(api.password, "another_password")
        self.assertEqual(api.username, "another_username")
        self.assertTrue(not api.authenticate)
        self.assertNotEqual(api.token, self.auth_token)

    def test_endpoint(self):
        new_api = Api(mode="live", username="dummy", password="dummy")
        self.assertEqual(new_api.endpoint, "http://dev.decktutor.com/ws-2.0/app/v2")
        self.assertEqual(new_api.token_endpoint, "http://dev.decktutor.com/ws-2.0/app/v2/account/login")

        new_api = Api(mode="sandbox", username="dummy", password="dummy")
        self.assertEqual(new_api.endpoint, "http://dev.decktutor.com/ws-2.0/app/v2")
        self.assertEqual(new_api.token_endpoint, "http://dev.decktutor.com/ws-2.0/app/v2/account/login")

        new_api = Api(endpoint="https://custom-endpoint.decktutor.com", username="dummy", password="dummy")
        self.assertEqual(new_api.endpoint, "https://custom-endpoint.decktutor.com")
        self.assertEqual(new_api.token_endpoint, "https://custom-endpoint.decktutor.com/account/login")

    def test_authenticate(self):
        new_api = Api(username="dummy", password="dummy")
        self.assertEqual(new_api.authenticate, False)

        new_api = Api(username="dummy", password="dummy", authenticate=True)
        self.assertEqual(new_api.authenticate, True)

    def test_get(self):
        self.api.request("/payments/payment?cnt=1", "GET")
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

    @mock.patch('decktutorsdk.api.Api.http_call', autospec=True)
    def test_expired_time(self, mock_http_call):
        old_date = '2012-12-31T11:09:45+00:00'
        token = {
            "auth_token": "test",
            "auth_token_expiration": old_date,
            "auth_token_secret": "test"
        }
        self.api.token = token
        new_token = self.api.get_token()
        self.assertNotEqual(token, new_token)

    @mock.patch('decktutorsdk.api.Api.http_call', autospec=True)
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

    def test_get_auth_token(self):
        with mock.patch("decktutorsdk.api.Api.http_call", autospec=True) as mock_http:
            mock_http.return_value = {
                'auth_token': self.auth_token,
                'auth_token_expiration': '2020-12-31T11:09:45+00:00',
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

        with mock.patch("decktutorsdk.api.Api.http_call", autospec=True) as mock_http:
            #Here the token should be valid
            auth_token = self.api.get_token()['auth_token']
            self.assertTrue(not mock_http.called)
            self.assertEqual(auth_token, self.auth_token)

    @mock.patch('decktutorsdk.api.Api.http_call', autospec=True)
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

    @mock.patch('decktutorsdk.api.Api.headers')
    @mock.patch('decktutorsdk.api.Api.http_call')
    def test_pagination_params(self, mock_http, mock_headers):

        mock_headers.return_value = {}
        url = "/endpoint"
        method = 'POST'
        api = Api(
            username=self.username, password=self.password, authenticate=True, endpoint=self.endpoint, mode="live"
        )
        api.request(url, method, 50, 1, {}, {}, {})
        mock_http.assert_called_once_with(self.endpoint+url, method, headers={},
                                          data='{}', params={
                                              'offset': 50,
                                              'limit': 99
                                          })

        api.request(url, method, 50, None, {}, {}, {})
        mock_http.assert_called_with(self.endpoint+url, method, headers={}, data='{}', params={})

        api.request(url, method, None, 0, {}, {}, {})
        mock_http.assert_called_with(self.endpoint+url, method, headers={}, data='{}', params={
            'offset': 0, 'limit': 99})
