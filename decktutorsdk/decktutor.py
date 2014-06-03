from decktutorsdk.api_map import API_MAP


class Decktutor(object):

    def __init__(self, api_map=API_MAP, **kwargs):
        """
        Create a Decktutor object used to call resolvers
        """
        self.api_map = api_map

    def __getattr__(self, name):
        if "url" in self.status:
            return ''
        else:
            # Default behaviour

            instance = Decktutor(status=2)
            setattr(self, name, instance)
            return instance



decktutor = Decktutor()
