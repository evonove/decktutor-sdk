from .api_map import api_map as global_map
from .exceptions import MissingConfig
from .resolvers import DefaultResolver
from . import utils

default_api_map = global_map["current"]["api"]


class Decktutor(object):
    """
    Simple decktutorsdk use:
    >>> decktutor.insertions.info(url_entry={'code':123}, params={'param1': 'abc', 'param2': 'def'})
    will call GET on http://dev.decktutor.com/ws-2.0/app/v2/insertions/123?param1=abc&param2=def
    """
    def __init__(self, api_map=None, **kwargs):
        """
        Create a Decktutor object used to call resolvers
        """
        self.api_map = api_map

    def __getattr__(self, name):
        if name not in self.api_map:
            raise MissingConfig("No sdk configuration found in api_map module for this call: " +
                                name)

        instance = Decktutor(api_map=self.api_map[name])
        # Cache the instance for current name
        setattr(self, name, instance)
        return instance

    def __call__(self, *args, **kwargs):
        #'url' is intended for internal mapping use only
        if 'url' not in self.api_map:
            raise MissingConfig("Cannot perform this call. Url param missing.")

        return self.get_resolver().resolve(api_map=self.api_map, **kwargs)

    def get_resolver_class(self):
        resolver_class = self.api_map.get('resolver')
        if resolver_class is None:
            return DefaultResolver

        return utils.load_class(resolver_class)

    def get_resolver(self):
        resolver_class = self.get_resolver_class()
        return resolver_class()


decktutor = Decktutor(api_map=default_api_map)
