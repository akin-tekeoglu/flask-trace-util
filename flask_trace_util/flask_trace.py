"""
Main class for trace operations
"""
from flask import g, request
import requests
from flask_trace_util.util import extract_gcloud_trace


class _FlaskTrace:
    def __init__(self, **kwargs):
        self.app = None
        self.extractor = kwargs.get("extractor")
        self.delegator = kwargs.get("delegator")
        self.user_id_extractor = kwargs.get("user_id_extractor")
        self.user_id_delegator = kwargs.get("user_id_delegator")

    def init_app(self, app, **kwargs):
        """
            Init app
        """
        self.app = app
        self.extractor = kwargs.get("extractor") or self.extractor
        self.delegator = kwargs.get("delegator") or self.delegator
        self.user_id_extractor = (
            kwargs.get("user_id_extractor") or self.user_id_extractor
        )
        self.user_id_delegator = (
            kwargs.get("user_id_delegator") or self.user_id_delegator
        )

        if self.app is None:
            raise Exception("app cant be None")

        if self.extractor is None:
            raise Exception("extractor cant be None")

        if self.delegator is None:
            raise Exception("delegator cant be None")

        @app.before_request
        def init_session():  # pylint: disable=unused-variable
            g.trace = self.extractor()
            if self.user_id_extractor:
                g.user_id = self.user_id_extractor()

        @app.after_request
        def destroy_session(
            response,
        ):  # pylint: disable=unused-variable,unused-argument
            g.trace = None
            return response

    def request(self, method, url, **kwargs):
        """Proxy request function which uses extracted trace field

        Arguments:
            method {string} -- http method
            url {string} -- url

        Returns:
            object -- requests response object
        """
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        header_name, header_value = self.delegator()
        kwargs["headers"][header_name] = header_value
        if self.user_id_delegator:
            u_header_name, u_header_value = self.user_id_delegator()
            kwargs["headers"][u_header_name] = u_header_value
        return requests.request(method, url, **kwargs)


def gcloud_trace_extractor(project_id):
    """Trace extractor for google cloud GKE

    Arguments:
        project_id {str} -- project id
    """

    def extractor():
        trace = request.headers.get("X-Cloud-Trace-Context")
        _, trace = extract_gcloud_trace(trace, project_id)
        return trace

    return extractor


def gcloud_trace_delegator():
    """Trace delegator for google cloud GKE

    Arguments:
        trace {str} -- trace
    """

    def delegator():
        trace = ""
        if g.trace:
            trace = g.trace.split("/")[-1]
        return "X-Cloud-Trace-Context", trace

    return delegator


def simple_user_id_extractor():
    """Simple user_id extractor
    """

    def extractor():
        user_id = request.headers.get("X-User-Id")
        return user_id

    return extractor


def simple_user_id_delegator():
    """Simple user_id delegator
    """

    def delegator():
        user_id = ""
        if g.user_id:
            user_id = g.user_id
        return "X-User-Id", user_id

    return delegator
