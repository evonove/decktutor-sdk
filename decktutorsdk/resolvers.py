from .api import api_factory
from decktutorsdk.exceptions import MissingParam


class BaseResolver(object):
    """
    Basic resolver Mixin.
    """

    def setup(self, api_map=None, url_entry=None, page_size=None):
        if api_map is None:
            raise Exception("Resolve must be called with 'api_map' argument")
        elif api_map.get('url') is None or api_map.get('method') is None:
            raise Exception("Resolve must be called with a map with 'url' and 'method'")

        url, method = api_map['url'], api_map['method']
        url_entry = url_entry or {}
        try:
            url = url.format(**url_entry)
        except KeyError as ke:
            raise MissingParam("Missing url sdk parameter: '%s'" % ke.message)
        self.url = url
        self.method = method
        self.page_size = api_map.get('page_size', page_size)


class DefaultResolver(BaseResolver):
    """
    Default resolver
    example Usage::
        BaseResolver(
            api_map={'url':'/{id}', 'method':'POST'}, url_entry={'id':123}, body={''}, params={''}
        ).resolve()
    """
    def resolve(self, api_map=None, url_entry=None, page=None, page_size=None, **kwargs):
        self.setup(api_map=api_map, url_entry=url_entry, page_size=page_size)

        return api_factory.get_instance(authenticate=False).request(
            url=self.url, method=self.method, page_size=self.page_size, page=page, **kwargs
        )


class AuthResolver(BaseResolver):
    """
    Auth resolver
    example Usage::
        AuthResolver(
            api_map={'url':'/authd/{id}', 'method':'POST'}, url_entry={'id':123}, body={''}, params={''}
        ).resolve()
    """
    def resolve(self, api_map=None, url_entry=None, page=None, page_size=None, **kwargs):
        self.setup(api_map=api_map, url_entry=url_entry, page_size=page_size)

        return api_factory.get_instance(authenticate=True).request(
            url=self.url, method=self.method, page_size=self.page_size, page=page, **kwargs
        )