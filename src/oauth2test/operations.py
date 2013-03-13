from oauth2test.check import CheckAuthorizationResponse
from oauth2test.check import CheckErrorResponseForInvalidType
from oauth2test.check import CheckErrorResponseForInvalidRedirect
from oauth2test.check import CheckSecondCodeUsageErrorResponse
from oauth2test.check import CheckPresenceOfStateParameter
from oauth2test.check import VerifyAccessTokenResponse
from rrtest.check import CheckHTTPResponse, VerifyError
from rrtest.request import BodyResponse
from rrtest.request import ErrorResponse
from rrtest.request import GetRequest
from rrtest.request import PostRequest
from rrtest.request import Response
from rrtest.request import UrlResponse


class AuthorizationRequest(GetRequest):
    request = "AuthorizationRequest"
    _request_args = {}
    tests = {"pre": [], "post": [CheckHTTPResponse]}


class AuthorizationRequestCode(AuthorizationRequest):
    _request_args = {"response_type": ["code"]}


class AccessTokenRequest(PostRequest):
    request = "AccessTokenRequest"
    _kw_args = {"authn_method": "client_secret_basic"}


class AuthorizationResponse(UrlResponse):
    response = "AuthorizationResponse"
    tests = {"post": [CheckAuthorizationResponse]}


class AccessTokenResponse(BodyResponse):
    response = "AccessTokenResponse"
    tests = {"post": [VerifyAccessTokenResponse]}


class AccessTokenSecondRequest(AccessTokenRequest):
    tests = {"post": [VerifyError]}

class AccessTokenSecondResponse(AccessTokenResponse):
    tests = {"post": [CheckSecondCodeUsageErrorResponse]}


class AuthorizationRequestCodeWithState(AuthorizationRequestCode):
    _request_args = AuthorizationRequestCode._request_args.copy()
    _request_args["state"] = "afdsliLKJ253oiuffaslkj"


class AuthorizationResponseWhichForcesState(AuthorizationResponse):
    tests = {"post": [CheckPresenceOfStateParameter]}


class AuthorizationRequestInvalidRedirectURI(AuthorizationRequestCode):
    """ Checks that the user isn't automatically redirected by the authorization
        provider to a faulty redirect_uri given by the client.
    """
    tests = {"post": [CheckErrorResponseForInvalidRedirect]}
    _request_args = AuthorizationRequestCode._request_args.copy()
    _request_args["redirect_uri"] = "http://localhost/invalid_xxxxxxxxxxxxxxxx"

class AuthorizationInvalidRedirectURIResponse(Response):
    """ Checks that the user isn't automatically redirected by the authorization
        provider to a faulty redirect_uri given by the client.
    """
    ctype = "unknown"
    where = "unknown"
    interaction_check = True
    tests = {}

    def from_unknown(self, *args, **kwargs):
        pass


class AccessTokenInvalidTypeRequest(AccessTokenRequest):
    tests = {"post": [VerifyError]}
    _request_args = AccessTokenRequest._request_args.copy()
    _request_args["grant_type"] = 'nissesapa'

class AccessTokenInvalidTypeResponse(ErrorResponse):
    tests = {"post": [CheckErrorResponseForInvalidType]}


class AuthorizationRequest2ndValidRedirectURI(AuthorizationRequestCode):
    """ Does a authorization code request. Used as a precursor to the second
        step which tries to request an access token with a different
        redirect_uri.
    """
    _request_args = AuthorizationRequestCode._request_args.copy()
    _request_args['redirect_uri'] = 'http://localhost:8081/second_valid'

class AccessTokenRequest1stValidRedirectURI(AccessTokenRequest):
    _request_args = AccessTokenRequest._request_args.copy()
    _request_args['redirect_uri'] = 'http://localhost:8081/'


PHASES = {
    "login": (AuthorizationRequestCode, AuthorizationResponse),
    "access-token-request": (AccessTokenRequest, AccessTokenResponse),
    "access-token-second-request": (AccessTokenSecondRequest,
                                        AccessTokenSecondResponse),
    "login-with-state": (AuthorizationRequestCodeWithState,
                AuthorizationResponseWhichForcesState),
    "login-with-invalid-redirect": (AuthorizationRequestInvalidRedirectURI,
                AuthorizationInvalidRedirectURIResponse),
    "login-with-2ndvalid-redirect": (AuthorizationRequest2ndValidRedirectURI,
                AuthorizationResponse),
    "access-token-request-invalid-type": (AccessTokenInvalidTypeRequest,
                        AccessTokenInvalidTypeResponse),
    "access-token-request-1stvalid-uri": (AccessTokenRequest1stValidRedirectURI,
                AccessTokenResponse),
}


FLOWS = {
    'code': {
        "name": 'Basic Code flow with authentication',
        "descr": ('Very basic test of a Provider using the authorization code ',
                  'flow. The test tool acting as a consumer is very relaxed',
                  'and tries to obtain an ID Token.'),
        "sequence": ["login"],
        "endpoints": ["authorization_endpoint"]
    },
    'code-idtoken_post': {
        "name": 'Basic Code flow with ID Token',
        "descr": ('Very basic test of a Provider using the authorization code ',
                  'flow. The test tool acting as a consumer is very relaxed',
                  'and tries to obtain an ID Token.'),
        "depends": ["basic-code-authn"],
        "sequence": ["login", "access-token-request"],
        "endpoints": ["authorization_endpoint", "token_endpoint"]
    },
    'code-idtoken-double_post': {
        "name": 'Basic Code flow with two requests for ID Token',
        "descr": ('Very basic test of a Provider using the authorization code ',
                  'flow. The test tool acting as a consumer is very relaxed',
                  'and tries to obtain an ID Token.'),
        "depends": ["basic-code-authn"],
        "sequence": ["login", "access-token-request",
            "access-token-second-request"],
        "endpoints": ["authorization_endpoint", "token_endpoint"]
    },
    'code-presence-of-state': {
        'name': 'Basic Code flow with authentication which checks for state parameter',
        'descr': ('Basic test of a Provider using the authorization code ',
                  'flow. The test tool acting as a consumer is relaxed but ',
                  'ensures that the state parameter in the authorization ',
                  'response is equal to the state given in the authorization ,'
                  'request.'),
        'sequence': ['login-with-state']
    },
    'code-verifies-redirect': {
        'name': 'Basic Code flow testing that the user agent isnt redirected to a faulty url',
        'descr': ('Basic test which tries to authenticate with a faulty',
                  'redirect_uri and makes sure that the user agent isnt',
                  'redirected to the faulty uri'),
        # Should also check that the user is informed of the error, but that
        # isn't possible,
        'sequence': ["login-with-invalid-redirect"]
    },
    'code-faulty-grant-type': {
        'name': 'Basic Code flow with faulty grant_type',
        'descr': ('Basic test of a Provider which checks that the provider',
                  'correctly indicates faulty values for the grant_type',
                  'parameter.'),
        'sequence': ['login', 'access-token-request-invalid-type'],
    },
    'code-different-redirect': {
        'name': 'Basic Code flow with different redirect_uri parameters',
        'descr': ("Uses a redirect which isn't the default but still valid.",
                  "Makes access token request with a different valid uri."),
        'sequence': ['login-with-2ndvalid-redirect',
            'access-token-request-1stvalid-uri'],
    },
}
