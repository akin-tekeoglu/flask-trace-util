"""
Main class for trace operations
"""
from flask import g, request
import requests

from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler


class _FlaskTrace:
    def __init__(self, **kwargs):
        self.app = None
        self.extractor = kwargs.get("extractor")
        self.delegator = kwargs.get("delegator")

    def init_app(self, app, **kwargs):
        """
            Init app
        """
        self.app = app
        self.extractor = kwargs.get("extractor") or self.extractor
        self.delegator = kwargs.get("delegator") or self.delegator

        if self.app is None:
            raise Exception("app cant be None")

        if self.extractor is None:
            raise Exception("extractor cant be None")

        if self.delegator is None:
            raise Exception("delegator cant be None")

        @app.before_request
        def init_session():  # pylint: disable=unused-variable
            trace_context = self.extractor()
            if "tracer" in trace_context:
                trace_context["tracer"].start_span(name=request.url)
            g.trace_context = trace_context

        @app.after_request
        def destroy_session(
            response,
        ):  # pylint: disable=unused-variable,unused-argument
            if g.trace_context and "tracer" in g.trace_context:
                g.trace_context["tracer"].tracer.finish()
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
        headers = self.delegator()
        for header_name, header_value in headers.items():
            kwargs["headers"][header_name] = header_value
        return requests.request(method, url, **kwargs)


def user_id_extractor():
    """Simple user_id extractor
    """

    def extractor():
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            user_id = "Anonymous"
        return "user_id", user_id

    return extractor


def user_id_delegator():
    """Simple user_id delegator
    """

    def delegator():
        user_id = "Anonymous"
        if g.trace_context and "user_id" in g.trace_context:
            user_id = g.trace_context["user_id"]
        return "X-User-Id", user_id

    return delegator


def opencencus_trace_extractor(exporter, header, propogator):
    def extractor():
        trace = request.headers.get(header)
        span_context = propogator.from_header(trace)
        tracer = Tracer(
            exporter=exporter, span_context=span_context, sampler=AlwaysOnSampler(),
        )
        return "tracer", tracer

    return extractor


def opencencus_trace_delegator(header, propogator):
    def delagator():
        trace = ""
        if g.trace_context and "tracer" in g.trace_context:
            span_context = g.trace_context["tracer"].span_context
            trace = propogator.to_header(span_context)
        return header, trace

    return delagator


def trace_extractor(extractors):
    def extractor():
        trace_context = {}
        for ex in extractors:
            k, val = ex()
            trace_context[k] = val
        return trace_context

    return extractor


def trace_delegator(delegators):
    def delegator():
        headers = {}
        for dele in delegators:
            k, val = dele()
            headers[k] = val
        return headers

    return delegator
