import unittest
from mock import patch
from decktutorsdk.decktutor import decktutor


class DecktutorTest(unittest.TestCase):

    def test_decktutor_instance_call(self):
        with patch("decktutorsdk.resolvers.AuthResolver.resolve") as mock_resolve:
            decktutor.insertions.info(url_entry={'code': 123})

            mock_resolve.assert_called_once_with(
                api_map=decktutor.api_map['insertions']['info'],
                url_entry={'code': 123}
            )
        with patch("decktutorsdk.resolvers.AuthResolver.resolve") as mock_resolve:
            decktutor.insertions.info(url_entry={'code': 123})

            mock_resolve.assert_called_once_with(
                api_map=decktutor.api_map['insertions']['info'],
                url_entry={'code': 123}
            )