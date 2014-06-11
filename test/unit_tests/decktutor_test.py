import unittest
from mock import patch
from decktutorsdk.api import Api, api_factory
from decktutorsdk.decktutor import Decktutor


class DecktutorTest(unittest.TestCase):

    def setUp(self):
        self.username = "test"
        self.password = "password"
        self.api = Api(
            username=self.username, password=self.password, authenticate=True
        )
        self.test_api_map = {
            'insertions': {
                'info': {
                    'url': '/insertions/{code}/',
                    'description': 'Retrieve basic information about an insertion',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                    'method': 'GET'
                }
            }
        }
        self.test_api_map_post = {
            'another': {
                'request': {
                    'url': '/things/{id}/url',
                    'description': 'Retrieve basic information about an insertion',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                    'method': 'POST'
                }
            }
        }
        self.test_api_map_def_resolver = {
            'account': {
                'login': {
                    'url': '/account/login',
                    'description': 'Create a logged in user session to authenticate future requests',
                    'method': 'POST'
                }
            }
        }
        self.api_factory = api_factory
        self.api_factory.configure(username=self.username, password=self.password)

    @patch("decktutorsdk.resolvers.AuthResolver.resolve")
    def test_auth_resolver_invocation(self, mock_resolve):

        decktutor = Decktutor(api_map=self.test_api_map)
        decktutor.insertions.info(url_entry={'code': 123})

        mock_resolve.assert_called_once_with(
            api_map=self.test_api_map['insertions']['info'],
            url_entry={'code': 123}
        )

    @patch("decktutorsdk.resolvers.DefaultResolver.resolve")
    def test_default_resolver_invocation(self, mock_resolve):

        decktutor = Decktutor(api_map=self.test_api_map_def_resolver)
        decktutor.account.login()

        mock_resolve.assert_called_once_with(
            api_map=self.test_api_map_def_resolver['account']['login']
        )

    @patch("decktutorsdk.api.Api.request")
    def test_request_get_invocation(self, mock_request):

        decktutor = Decktutor(api_map=self.test_api_map)
        decktutor.insertions.info(url_entry={'code': 123})

        mock_request.assert_called_once_with(
            url="/insertions/123/", method="GET"
        )

    @patch("decktutorsdk.api.Api.request")
    def test_request_get_invocation_params(self, mock_request):

        decktutor = Decktutor(api_map=self.test_api_map)
        decktutor.insertions.info(url_entry={'code': 456}, params={'param1': 'abc'})

        mock_request.assert_called_once_with(
            url="/insertions/456/", method="GET", params={'param1': 'abc'}
        )

    @patch("decktutorsdk.api.Api.request")
    def test_request_post_invocation(self, mock_request):

        decktutor = Decktutor(api_map=self.test_api_map_post)
        decktutor.another.request(url_entry={'id': 123})

        mock_request.assert_called_once_with(
            url="/things/123/url", method="POST"
        )

    @patch("decktutorsdk.api.Api.request")
    def test_request_post_body_invocation(self, mock_request):

        decktutor = Decktutor(api_map=self.test_api_map_post)
        decktutor.another.request(url_entry={'id': 123}, body="my_body", params={"param1": "param"}, headers="head")

        mock_request.assert_called_once_with(
            url="/things/123/url", method="POST", body="my_body", params={"param1": "param"}, headers="head"
        )

