from api_map import api_map as global_map
from decktutorsdk.exceptions import MissingConfig
from decktutorsdk.resolvers import DefaultResolver
import decktutorsdk.utils as util

api_config = global_map["current"]["api"]


class Decktutor(object):

    """
    Simple decktutorsdk use:
    >>> decktutor.insertions.info(url_entry={'code':123}, params={'param1': 'abc', 'param2': 'def'})
    will call   GET   on   http://dev.decktutor.com/ws-2.0/app/v2/insertions/123?param1=abc&param2=def
    """
    def __init__(self, api_map=None, **kwargs):
        """
        Create a Decktutor object used to call resolvers
        """
        self.api_map = api_map

    def __getattr__(self, name):

        if name not in self.api_map:
            raise MissingConfig("No sdk configuration found in api_map module for this call: " + name)

        # Default behaviour
        instance = Decktutor(api_map=self.api_map[name])
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

        return util.load_class(resolver_class)

    def get_resolver(self):
        resolver_class = self.get_resolver_class()
        return resolver_class()


decktutor = Decktutor(api_map=api_config)
