import os
from decktutorsdk import exceptions
from decktutorsdk.api import Api


class BaseResolver(object):
    """
    This is the very basic resolver
    """

    def resolve(self):
        raise NotImplementedError(
            "You have to call am instance of an implemented Resolver"
        )


class DefaultResolver(object):
    """
    Default resolver
    """

    def resolve(self):
        pass


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
    __auth_api__ = Api(options or {}, **config)
    return __auth_api__


def set_default_config(options=None, **config):
    """
    Create new default api object with given configuration
    """
    global __auth_api__
    __auth_api__ = Api(options or {}, **config)
    return __auth_api__

