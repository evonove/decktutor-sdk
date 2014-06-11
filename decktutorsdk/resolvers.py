from decktutorsdk.api import api_factory


class BaseResolver(object):
    """
    This is the basic resolver
    Does nothing
    """
    def resolve(self, api_map=None, url_entry=None):
        if api_map is None:
            raise Exception("Resolve must be called with 'api_map' argument")
        elif api_map.get('url') is None or api_map.get('method') is None:
            raise Exception("Resolve must be called with a map with 'url' and 'method'")

        url, method = api_map['url'], api_map['method']
        url_entry = url_entry or {}
        url = url.format(**url_entry)
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
        return api_factory.get(authenticate=False).request(url=url, method=method, **kwargs)


class AuthResolver(BaseResolver):
    """
    Auth resolver
    example Usage::
    >>> resolve(
    >>>     api_map={'url':'/authd/{id}', 'method':'POST'}, url_entry={'id':123}, body={''}, params={''}
    >>> )
    """
    def resolve(self, api_map=None, url_entry=None, **kwargs):
        url, method = super(AuthResolver, self).resolve(api_map=api_map, url_entry=url_entry)
        return api_factory.get(authenticate=True).request(url=url, method=method, **kwargs)
