from api_map import api_map
from decktutorsdk.resolvers import DefaultResolver
import decktutorsdk.util as util


class Decktutor(object):

    def __init__(self, api_map=api_map, **kwargs):
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

            instance = Decktutor(status=2)
            setattr(self, name, instance)
            return instance


decktutor = Decktutor()
