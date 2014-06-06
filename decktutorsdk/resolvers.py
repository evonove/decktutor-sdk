import os
from decktutorsdk import exceptions
from decktutorsdk.api import Api


class BaseResolver(object):
    """
    This is the very basic resolver
    Does nothing
    """

    def resolve(self, api_map=None, url_entry=None):
        if api_map is None:
            raise Exception("Resolve must be called with 'api_map' argument")
        elif api_map['url'] is None or api_map['method']:
            raise Exception("Resolve must be called with a map with 'url' and 'method'")

        url, method = api_map['url'], api_map['method']
        url_entry = url_entry or {}
        url = url.format(url_entry)
        return url, method


class DefaultResolver(BaseResolver):
    """
    Default resolver
    example Usage::
    >>> resolve(
    >>>     api_map={'url':'/{id}', 'method':'POST'}, url_entry={'id':123}, body={''}, params={''}
    >>> )
    """

    def resolve(self, api_map=None, url_entry=None, **kwargs):
        url, method = super(DefaultResolver, self).resolve(api_map=api_map, url_entry=url_entry)
        default().request(url=url, method=method, **kwargs)


class AuthResolver(BaseResolver):
    """
    Auth resolver
    example Usage::
    >>> resolve(
    >>>     api_map={'url':'/authd/{id}', 'method':'POST'}, url_entry={'id':123}, body={''}, params={''}
    >>> )
    """

    def resolve(self, api_map=None, url_entry=None, **kwargs):
        url, method = super(DefaultResolver, self).resolve(api_map=api_map, url_entry=url_entry)
        default_auth().request(url=url, method=method, **kwargs)


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

