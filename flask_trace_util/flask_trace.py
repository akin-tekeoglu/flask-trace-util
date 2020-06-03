"""
Main class for trace operations
"""
from flask import g, request
import requests
from flask_trace_util.util import extract_gcloud_trace


class _FlaskTrace:
    def __init__(self):
        self.app = None
        self.extractor = None
        self.delegator = None

    def init_app(self, app, extractor=None, delegator=None):
        """
            Init app
        """
        self.app = app
        self.extractor = extractor = extractor
        self.delegator = delegator
        if app is None:
            raise Exception("app cant be None")

        if extractor is None:
            raise Exception("extractor cant be None")

        if delegator is None:
            raise Exception("delegator cant be None")

        @app.before_request
        def init_session():  # pylint: disable=unused-variable
            g.trace = extractor()

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
        if g.trace:
            header = g.trace.split("/")[-1]
            return "X-Cloud-Trace-Context", header
        else:
            return "X-Cloud-Trace-Context", ""

    return delegator
