import os
from api_map import api_map as global_map
from decktutorsdk import exceptions
from decktutorsdk.api import Api
from decktutorsdk.resolvers import DefaultResolver
import decktutorsdk.util as util

global_map = global_map["current"]


class Decktutor(object):

    def __init__(self, api_map=global_map, **kwargs):
        """
        Create a Decktutor object used to call resolvers
        """
        self.api_map = api_map

    def __getattr__(self, name):

        #'url' is intended for internal mapping use only
        if self.api_map['url']:
            resolver_class = self.api_map['resolver']
            if resolver_class:
                resolver = util.load_class(resolver_class)()
            else:
                resolver = DefaultResolver()
            return resolver.resolve
        else:
            # Default behaviour

            instance = Decktutor(api_map=self.api_map[name])
            setattr(self, name, instance)
            return instance


__auth_api__ = None
__api__ = None


def default_auth():
    """
    Returns the auth api object and if not present creates a new one
    """
    global __auth_api__
    if __auth_api__ is None:
        try:

            username = os.environ["DECKTUTOR_USERNAME"]
            password = os.environ["DECKTUTOR_PASSWORD"]
        except KeyError:
            raise exceptions.MissingConfig(
                "DECKTUTOR_USERNAME and DECKTUTOR_PASSWORD not provided!"
            )

        __auth_api__ = Api(mode=os.environ.get("DECKTUTOR_MODE", "sandbox"),
                           username=username, password=password, authenticate=True)
    return __auth_api__


def default():
    """
    Returns default api object and if not present creates a new one
    """
    global __api__
    if __api__ is None:

        __api__ = Api(mode=os.environ.get("DECKTUTOR_MODE", "sandbox"),
                      authenticate=False)
    return __auth_api__


def set_auth_config(options=None, **config):
    """
    Create new api object with given configuration and authentication
    """
    global __auth_api__
    __auth_api__ = Api(options or {}, authenticate=True, **config)
    return __auth_api__


def set_default_config(options=None, **config):
    """
    Create new default api object with given configuration
    """
    global __auth_api__
    __auth_api__ = Api(options or {}, authenticate=False, **config)
    return __auth_api__


decktutor = Decktutor()
