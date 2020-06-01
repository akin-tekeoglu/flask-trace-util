"""
Main class for trace operations
"""
from flask import g
import requests


class _FlaskTrace:
    def __init__(self):
        self.app = None
        self.config = None

    def init_app(self, app, config):
        """Init app

        Arguments:
            app {object} -- flask app
            config {object} -- trace configuration

        """
        self.app = app
        self.config = config
        if app is None:
            raise Exception("app cant be None")

        if config is None:
            raise Exception("config cant be None")

        if "extractor" not in config:
            raise Exception(
                "config must include extractor key for header extraction process"
            )

        if "delegator" not in config:
            raise Exception(
                "config must include delegator key for trace delegation to subsequent requests"
            )

        @app.before_request
        def init_session():  # pylint: disable=unused-variable
            g.trace = config["extractor"]()

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
        header_name, header_value = self.config["delegator"]()
        kwargs["headers"][header_name] = header_value
        return requests.request(method, url, **kwargs)


flask_trace = _FlaskTrace()
