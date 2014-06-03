from api_map import api_map


class Decktutor(object):

    def __init__(self, api_map=api_map, **kwargs):
        """
        Create a Decktutor object used to call resolvers
        """
        self.api_map = api_map

    def __getattr__(self, name):

        #'url' is intended for internal mapping use only
        if self.api_map['url']:
            return ''

        else:
            # Default behaviour

            instance = Decktutor(status=2)
            setattr(self, name, instance)
            return instance


decktutor = Decktutor()
