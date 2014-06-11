import hashlib
import requests
import json
import logging
import os
import datetime
import time
from decktutorsdk.api_map import api_map

import decktutorsdk.util as util

from decktutorsdk import exceptions
from decktutorsdk.version import __version__

api_map = api_map["current"]

var_username = "DECKTUTOR_USERNAME"
var_password = "DECKTUTOR_PASSWORD"
var_mode = "DECKTUTOR_MODE"


class Api(object):

    user_agent = "decktutor-sdk/evonove(version=%s)" % __version__

    def __init__(self, options=None, **kwargs):
        """
        Create API object
        """
        kwargs = util.merge_dict(options or {}, kwargs)

        #required params
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        #end required

        self.authenticate = kwargs.get("authenticate", False)
        self.mode = kwargs.get("mode", "sandbox")
        self.endpoint = kwargs.get("endpoint", self.default_endpoint())
        self.token_endpoint = kwargs.get("token_endpoint", self.default_token_endpoint(base=self.endpoint))
        self.token = None
        self.token_request_at = None
        self.incremental = int(time.time())
        # setup SSL certificate verification if private certificate provided
        ssl_options = kwargs.get("ssl_options", {})
        if "cert" in ssl_options:
            os.environ["REQUESTS_CA_BUNDLE"] = ssl_options["cert"]

        self.options = kwargs

    def default_endpoint(self):

        if self.mode == "live":
            return api_map["api_root"]
        else:
            return api_map["api_sandbox_root"]

    def default_token_endpoint(self, base=None):

        if not base:
            base = self.default_endpoint()
        return base+api_map['api']['account']['login']['url']

    def basic_auth(self):
        """
        Find basic auth, and returns base64 encoded
        """
        credentials = '{"login":"%s", "password":"%s"}' % (self.username, self.password)
        #base64 case
        #return base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return credentials

    def get_token(self):
        """
        Generate new token by making a POST request
        """
        payload = self.basic_auth()

        self.validate_token_hash()
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

    def validate_token_hash(self):
        """Checks if token duration has expired and if so resets token
        """
        if self.token and self.token.get("auth_token_expiration") is not None:
            if datetime.datetime.now() > util.parse_datetime(self.token.get("auth_token_expiration")):
                self.token = None

    def request(self, url, method, headers=None, body=None, params=None):
        """
        Make HTTP call, formats response and does error handling. Uses http_call method in API class.
        'body' param will be JSONyfied!
        Usage::
            >>> api.request("/things", "GET", {})
            >>> api.request("/other/things", "POST", "{}", {} )
        """
        http_headers = util.merge_dict(self.headers(), headers or {})
        url = self.endpoint+url
        try:
            return self.http_call(url, method, data=json.dumps(body), params=params, headers=http_headers)

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
        return self.handle_response(response, response.content.decode('utf-8'))

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

    def headers(self, authenticate=None):

        if authenticate is None:
            authenticate = self.authenticate

        if authenticate:
            token = self.get_token()
            sequence = self.sequence_number()
            headers = {
                "x-dt-Auth-Token": ("%s" % token['auth_token']),
                "x-dt-Signature": (
                    "%s" % hashlib.md5("%02d:%s" % (sequence, token['auth_token_secret'])).hexdigest()
                ),
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

    def get(self, authenticate=False):
        """
        Returns the  api object and if not present creates a new one.
        Mode var is lazy loaded by the api, if none --> 'sandbox'
        """
        if not self._username or not self._password:
            try:

                self._username = os.environ[var_username]
                self._password = os.environ[var_password]
                self._mode = os.environ.get(var_mode)
            except KeyError:
                raise exceptions.MissingConfig(
                    "%s and %s not provided!" % (var_username, var_password)
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