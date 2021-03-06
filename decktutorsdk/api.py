import hashlib
import requests
import json
import logging
import os
import datetime
import time

from . import utils
from . import exceptions
from .api_map import api_map
from .version import __version__


class Api(object):
    """
    Api object for internal api authentication, exceptions handling,
     logging and api response presentation purpose
    """
    user_agent = "decktutor-sdk/evonove(version=%s)" % __version__

    def __init__(self, options=None, **kwargs):
        kwargs = utils.merge_dict(options or {}, kwargs)
        #required params
        self.username = kwargs["username"]
        self.password = kwargs["password"]

        self.api_map = api_map["current"]
        self.authenticate = kwargs.get("authenticate", False)
        self.mode = kwargs.get("mode", "sandbox")
        self.endpoint = kwargs.get("endpoint", self.default_endpoint())
        self.token_endpoint = kwargs.get("token_endpoint", self.default_token_endpoint(base=self.endpoint))
        self.token = None
        self.page_size = self.default_page_size()
        self.token_request_at = None
        self.incremental = int(time.time())
        # setup SSL certificate verification if private certificate provided
        ssl_options = kwargs.get("ssl_options", {})
        if "cert" in ssl_options:
            os.environ["REQUESTS_CA_BUNDLE"] = ssl_options["cert"]

        self.options = kwargs

    def default_endpoint(self):
        if self.mode == "live":
            return self.api_map["api_root"]
        else:
            return self.api_map["api_sandbox_root"]

    def default_token_endpoint(self, base=None):
        if base is None:
            base = self.default_endpoint()
        return base + self.api_map['api']['account']['login']['url']

    def default_page_size(self):
        """
        Return the default configured pagesize or the default for decktutor api
        """
        return self.api_map['api_page_size'] or 100

    def basic_auth(self):
        """
        Find basic auth
        """
        credentials = '{{"login":"{username}", "password":"{password}"}}'.format(
            username=self.username, password=self.password
        )
        return credentials

    def get_token(self):
        """
        Generate new token by making a POST request
        """
        payload = self.basic_auth()

        self._validate_token_hash()
        if self.token is not None:
            return self.token
        else:
            self.token_request_at = datetime.datetime.now()

        login = self.http_call(
            self.token_endpoint, "POST",
            data=payload,
            headers=self.headers(authenticate=False))

        self.token = login
        return self.token

    def sequence_number(self):
        """
        return an incremental number, dependent on timestamp getted on the api init call
        """
        self.incremental += 1
        return self.incremental

    def _validate_token_hash(self):
        """
        Checks if token duration has expired and if so resets token
        """
        if self.token and self.token.get("auth_token_expiration") is not None:
            date = utils.parse_datetime(self.token.get("auth_token_expiration"))
            if utils.time_now() > date:
                self.token = None

    def request(self, url, method, page_size=None, page=None, headers=None, body=None, params=None):
        """
        Make HTTP call, formats response and does error handling. Uses http_call method in API class.
        'body' param will be JSONyfied!
        Usage::
            api.request("/things", "GET", {})
            api.request("/other/things", "POST", "{}", {} )
        """
        http_headers = utils.merge_dict(self.headers(), headers or {})
        params = utils.merge_dict(self.pagination_params(page, page_size), params or {})
        url = self.endpoint+url
        try:
            response = self.http_call(
                url, method, data=json.dumps(body), params=params, headers=http_headers
            )
            if self.mode == "sandbox":
                self.write_response_file(response, url)

            return response

        # Format Error message for bad request
        except exceptions.BadRequest as error:
            return {"error": json.loads(error.content)}

        # Handle Expired token
        except exceptions.UnauthorizedAccess as error:
            if self.token and self.username and self.password:
                self.token = None
                return self.request(url, method, body, headers)
            else:
                raise error

    def http_call(self, url, method, **kwargs):
        """
        Makes a http call with logging.
        """
        logging.info('Request[%s]: %s' % (method, url))
        start_time = datetime.datetime.now()

        response = requests.request(method, url, **kwargs)

        duration = datetime.datetime.now() - start_time
        logging.info('Response[%d]: %s, Duration: %s.%ss.' % (
            response.status_code, response.reason, duration.seconds, duration.microseconds
        ))
        #In case of content in the response is UTF-8 encoded use:
        #>>> response.content.decode('utf-8')
        return self.handle_response(response, response.content.decode('utf-8'))

    def write_response_file(self, json_res, title):
        fname = '{}_{:%Y%m%d%H%M%S}_.xml'.format(title.split("/")[-1], datetime.datetime.now())
        fname = os.path.join(os.path.dirname(os.path.realpath(__file__)), fname)
        with open(fname, 'w') as ofile:
            text = json.dumps(json_res, indent=4, sort_keys=True)
            ofile.write(text)

    def handle_response(self, response, content):
        """
        Check the HTTP response
        """
        status = response.status_code
        if status in (301, 302, 303, 307):
            raise exceptions.Redirection(response, content)
        elif 200 <= status <= 299:
            return json.loads(content) if content else {}
        elif status == 400:
            raise exceptions.BadRequest(response, content)
        elif status == 401:
            raise exceptions.UnauthorizedAccess(response, content)
        elif status == 403:
            raise exceptions.ForbiddenAccess(response, content)
        elif status == 404:
            raise exceptions.ResourceNotFound(response, content)
        elif status == 405:
            raise exceptions.MethodNotAllowed(response, content)
        elif status == 409:
            raise exceptions.ResourceConflict(response, content)
        elif status == 410:
            raise exceptions.ResourceGone(response, content)
        elif status == 422:
            raise exceptions.ResourceInvalid(response, content)
        elif 401 <= status <= 499:
            raise exceptions.ClientError(response, content)
        elif 500 <= status <= 599:
            raise exceptions.ServerError(response, content)
        else:
            raise exceptions.ConnectionError(response, content, "Unknown response code: #{response.code}")

    def pagination_params(self, page=None, page_size=None):
        """
        Pages start from page 0 to +
        """
        if page is None:
            return {}

        if page_size is None:
            page_size = self.page_size
        page_size = int(page_size)
        offset = int(page) * page_size
        limit = offset + page_size - 1
        return {
            'offset': offset,
            'limit': limit
        }

    def headers(self, authenticate=None):
        if authenticate is None:
            authenticate = self.authenticate

        if authenticate:
            token = self.get_token()
            sequence = self.sequence_number()
            signature = ("%02d:%s" % (sequence, token['auth_token_secret'])).encode("UTF-8")
            headers = {
                "x-dt-Auth-Token": ("%s" % token['auth_token']),
                "x-dt-Signature": ("%s" % hashlib.md5(signature).hexdigest()),
                "x-dt-Sequence": ("%s" % sequence),
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": self.user_agent
            }
        else:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": self.user_agent
            }
        return headers


class ApiFactory(object):
    """
    Create new ApiFactory object with given configuration
    """
    def __init__(self):
        self._api = None
        self._auth_api = None
        self._username = None
        self._password = None
        self._mode = None

    def get_instance(self, authenticate=True):
        """
        Returns the  api object and if not present creates a new one.
        Mode var is lazy loaded by the api, if none --> 'sandbox'
        """
        if not self._username or not self._password:
            try:

                self._username = os.environ["DECKTUTOR_USERNAME"]
                self._password = os.environ["DECKTUTOR_PASSWORD"]
                self._mode = os.environ.get("DECKTUTOR_MODE")
            except KeyError:
                raise exceptions.MissingConfig(
                    "You have to set DECKTUTOR_USERNAME and DECKTUTOR_PASSWORD env vars or call"
                    "api_factory.configure() method."
                )
        if not authenticate:
            if self._api is None:
                self._api = Api(mode=self._mode, username=self._username,
                                password=self._password, authenticate=authenticate)
            return self._api

        if self._auth_api is None:
            self._auth_api = Api(mode=self._mode, username=self._username,
                                 password=self._password, authenticate=authenticate)
        return self._auth_api

    def configure(self, username=None, password=None, mode=None, api=None, auth_api=None):
        """
        Configure the api before get()
        """
        self._api = api or self._api
        self._auth_api = auth_api or self._auth_api
        self._username = username
        self._password = password
        self._mode = mode

api_factory = ApiFactory()

