import os
from api_map import api_map as global_map
from decktutorsdk import exceptions
from decktutorsdk.api import Api
from decktutorsdk.exceptions import MissingConfig
from decktutorsdk.resolvers import DefaultResolver
import decktutorsdk.util as util

api_config = global_map["current"]["api"]


class Decktutor(object):

    """
    Simple decktutorsdk use:
    >>> decktutor.insertions.info(url_entry={'code':123}, params={'param1': 'abc', 'param2': 'def'})
    will call   GET   on   http://dev.decktutor.com/ws-2.0/app/v2/insertions/123?param1=abc&param2=def
    """
    def __init__(self, api_map=api_config, **kwargs):
        """
        Create a Decktutor object used to call resolvers
        """
        self.api_map = api_map
        self.resolver = None

    def __getattr__(self, name):

        self.api_map = self.api_map[name]
        #'url' is intended for internal mapping use only
        if self.api_map.get('url'):
            resolver_class = self.api_map.get('resolver')
            if resolver_class:
                resolver = util.load_class(resolver_class)()
            else:
                resolver = DefaultResolver()
            self.resolver = resolver
            return self.resolve_proxy
        else:
            # Default behaviour
            try:
                instance = Decktutor(api_map=self.api_map)
                setattr(self, name, instance)
                return instance
            except KeyError:
                raise MissingConfig('No sdk configuration found in api_map module for this call: %s' % name)

    def resolve_proxy(self, **kwargs):
        return self.resolver.resolve(api_map=self.api_map, **kwargs)


decktutor = Decktutor()
