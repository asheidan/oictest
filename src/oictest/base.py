#!/usr/bin/env python
__author__ = 'rohe0002'

import sys

from oic.oauth2.message import Message
from oic.oic import RegistrationResponse

from rrtest import tool, FatalError

ORDER = ["url", "response", "content"]


def endpoint(client, base):
    for _endp in client._endpoints:
        if getattr(client, _endp) == base:
            return True

    return False


class Conversation(tool.Conversation):
    def __init__(self, client, config, trace, interaction, msg_factory,
                 check_factory, features=None, verbose=False,
                 expect_exception=False):
        tool.Conversation.__init__(self, client, config, trace,
                                   interaction, check_factory, msg_factory,
                                   features, verbose, expect_exception)
        self.cis = []
        #self.item = []
        self.keyjar = self.client.keyjar
        self.position = ""
        self.last_response = None
        self.last_content = None
        self.accept_exception = False
        self.creq = None
        self.cresp = None
        self.msg_factory = msg_factory
        self.login_page = None
        self.response_message = None

    def my_endpoints(self):
        return self.client.redirect_uris

    def handle_result(self):
        try:
            self.response_spec = resp = self.cresp()
        except TypeError:
            self.response_spec = None
            return True

        self.info = None
        self.response_message = None

        response = self.last_response
        resp_type = resp.ctype
        if response:
            try:
                ctype = response.headers["content-type"]
                if ctype == "application/jwt":
                    resp_type = "jwt"
            except (AttributeError, TypeError):
                pass

        if response.status_code >= 400:
            pass
        elif not self.position:
            if isinstance(self.last_content, Message):
                self.response_message = self.last_content
            elif response.status_code == 200:
                self.info = self.last_content
        elif resp.where == "url" or response.status_code == 302:
            try:
                self.info = response.headers["location"]
                resp_type = "urlencoded"
            except KeyError:
                try:
                    _check = getattr(self.creq, "interaction_check", None)
                except AttributeError:
                    _check = None

                if _check:
                    self.err_check("interaction-check")
                else:
                    self.do_check("missing-redirect")
        else:
            self.do_check("check_content_type_header")
            self.info = self.last_content

        if self.info and resp.response:
            if isinstance(resp.response, basestring):
                response = self.msg_factory(resp.response)
            else:
                response = resp.response

            self.response_type = response.__name__
            try:
                _qresp = self.client.parse_response(
                    response, self.info, resp_type, self.client.state,
                    keyjar=self.keyjar, client_id=self.client.client_id,
                    scope="openid")
                self.trace.info("[%s]: %s" % (_qresp.type(), _qresp.to_dict()))
                #item.append(qresp)
                self.response_message = _qresp
                self.protocol_response.append((_qresp, self.info))
                err = None
            except Exception, err:
                self.exception = "%s" % err

            if err and self.accept_exception:
                if isinstance(err, self.accept_exception):
                    self.trace.info("Got expected exception: %s [%s]" % (
                        err, err.__class__.__name__))
                else:
                    raise
            else:
                self.do_check("response-parse")

        return self.post_process(resp)

    def post_process(self, resp):
        if self.response_message:
            try:
                self.test_sequence(resp.tests["post"])
            except KeyError:
                pass

            if isinstance(self.response_message, RegistrationResponse):
                for key, val in self.response_message.items():
                    setattr(self.client, key, val)

            resp(self, self.response_message)

            return True
        else:
            return False

    def send(self):
        try:
            self.test_sequence(self.req.tests["pre"])
        except KeyError:
            pass

        try:
            if self.verbose:
                print >> sys.stderr, "> %s" % self.req.request
            part = self.req(self.position, self.last_response,
                            self.last_content, self.features)
            (self.position, self.last_response, self.last_content) = part

            try:
                if not self.test_sequence(self.req.tests["post"]):
                    self.position = None
            except KeyError:
                pass
        except FatalError:
            raise
        except Exception, err:
            self.err_check("exception", err)
