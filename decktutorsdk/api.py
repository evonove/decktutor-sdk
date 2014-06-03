import requests
import json
import logging
import os
import datetime
import time
from decktutorsdk.exceptions import MissingConfig

import decktutorsdk.util as util

from decktutorsdk import exceptions
from decktutorsdk.version import __version__

DECKTUTOR_V2 = "http://dev.decktutor.com/ws-2.0/app/v2"
DECKTUTOR_SANDBOX_V2 = "http://dev.decktutor.com/ws-2.0/app/v2"


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
        self.mode = kwargs.get("mode", "sandbox")
        self.endpoint = kwargs.get("endpoint", self.default_endpoint())
        self.token_endpoint = kwargs.get("token_endpoint", self.endpoint)
        self.token_hash = None
        self.token_request_at = None
        self.incremental = time.time()
        # setup SSL certificate verification if private certificate provided
        ssl_options = kwargs.get("ssl_options", {})
        if "cert" in ssl_options:
            os.environ["REQUESTS_CA_BUNDLE"] = ssl_options["cert"]

        if kwargs.get("token"):
            self.token_hash = {"access_token": kwargs["token"], "token_type": "Bearer"}

        self.options = kwargs

    def default_endpoint(self):

        if self.mode == "live":
            return DECKTUTOR_V2
        else:
            return DECKTUTOR_SANDBOX_V2

    def basic_auth(self):
        """Find basic auth, and returns base64 encoded
        """
        credentials = "%s:%s" % (self.username, self.password)
        return base64.b64encode(credentials.encode('utf-8')).decode('utf-8').replace("\n", "")

    def get_token_hash(self, authorization_code=None, refresh_token=None):
        """Generate new token by making a POST request

            1. By using client credentials if validate_token_hash finds
            token to be invalid. This is useful during web flow so that an already
            authenticated user is not reprompted for login
            2. Exchange authorization_code from mobile device for a long living
            refresh token that can be used to charge user who has consented to future
            payments
            3. Exchange refresh_token for the user for a access_token of type Bearer
            which can be passed in to charge user

        """
        path = "/account/login"
        payload = "grant_type=client_credentials"

        if authorization_code is not None:
            payload = "grant_type=authorization_code&response_type=token&redirect_uri=urn:ietf:wg:oauth:2.0:oob&code=" + authorization_code

        elif refresh_token is not None:
            payload = "grant_type=refresh_token&refresh_token=" + refresh_token

        else:
            self.validate_token_hash()
            if self.token_hash is not None:
                return self.token_hash
            else:
                self.token_request_at = datetime.datetime.now()

        self.token_hash = self.http_call(
            util.join_url(self.token_endpoint, path), "POST",
            data=payload,
            headers={
                "Authorization": ("Basic %s" % self.basic_auth()),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json", "User-Agent": self.user_agent
            })

        return self.token_hash

    def sequence_number(self):
        """
        return an incremental number, dependent on timestamp getted on the api init call
        """
        return self.incremental + 1

    def validate_token_hash(self):
        """Checks if token duration has expired and if so resets token
        """
        if self.token_request_at and self.token_hash and self.token_hash.get("expires_in") is not None:
            delta = datetime.datetime.now() - self.token_request_at
            duration = (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 10**6
            if duration > self.token_hash.get("expires_in"):
                self.token_hash = None

    def get_refresh_token(self, authorization_code=None):
        if authorization_code is None:
            raise exceptions.MissingConfig("Authorization code needed to get new refresh token. Refer to https://developer.paypal.com/docs/integration/mobile/make-future-payment/#get-an-auth-code")
        return self.get_token_hash(authorization_code)["refresh_token"]

    def request(self, url, method, body=None, headers=None, refresh_token=None):
        """Make HTTP call, formats response and does error handling. Uses http_call method in API class.

        Usage::

            >>> api.request("https://api.sandbox.paypal.com/v1/payments/payment?count=10", "GET", {})
            >>> api.request("https://api.sandbox.paypal.com/v1/payments/payment", "POST", "{}", {} )

        """

        http_headers = util.merge_dict(self.headers(refresh_token=refresh_token), headers or {})

        if http_headers.get('PayPal-Request-Id'):
            logging.info('PayPal-Request-Id: %s' % (http_headers['PayPal-Request-Id']))

        try:
            return self.http_call(url, method, data=json.dumps(body), headers=http_headers)

        # Format Error message for bad request
        except exceptions.BadRequest as error:
            return {"error": json.loads(error.content)}

        # Handle Expired token
        except exceptions.UnauthorizedAccess as error:
            if(self.token_hash and self.username):
                self.token_hash = None
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

    def headers(self, refresh_token=None):

        token_hash = self.get_token_hash(refresh_token=refresh_token)

        return {
            "x-dt-Auth-Token": ("%s" % token_hash['auth_token']),
            "x-dt-Signature": ("%s" % self.sequence_number()),
            "x-dt-Sequence": ("%s" % token_hash['signed_token']),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent
        }

    def get(self, action, headers=None):

        return self.request(util.join_url(self.endpoint, action), 'GET', headers=headers or {})

    def post(self, action, params=None, headers=None, refresh_token=None):

        return self.request(util.join_url(self.endpoint, action), 'POST', body=params or {},
                            headers=headers or {}, refresh_token=refresh_token)

    def put(self, action, params=None, headers=None, refresh_token=None):

        return self.request(util.join_url(self.endpoint, action), 'PUT', body=params or {},
                            headers=headers or {}, refresh_token=refresh_token)

    def delete(self, action, headers=None):

        return self.request(util.join_url(self.endpoint, action), 'DELETE', headers=headers or {})


#the global decktutor api!
__api__ = None


def default():
    """
    Returns default api object and if not present creates a new one
    """
    global __api__
    if __api__ is None:
        try:

            username = os.environ["DECKTUTOR_USERNAME"]
            password = os.environ["DECKTUTOR_PASSWORD"]
        except KeyError:
            raise exceptions.MissingConfig(
                "DECKTUTOR_USERNAME and DECKTUTOR_PASSWORD not provided!"
            )

        __api__ = Api(mode=os.environ.get("DECKTUTOR_MODE", "sandbox"),
                      username=username, password=password)
    return __api__


def set_config(options=None, **config):
    """
    Create new default api object with given configuration
    """
    global __api__
    __api__ = Api(options or {}, **config)
    return __api__

configure = set_config