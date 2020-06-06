from flask import g, request
import requests

class NoopTracer:
    def __getattr__(self, item):
        return None

class Requests:

    def _request(method,headers):

        def __request(self,url,**kwargs):
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            for header_name, header_value in headers.items():
                kwargs["headers"][header_name] = header_value
            return requests.request(method, url, **kwargs)
        
        def __getattr__(self, item):
            return None

class FlaskTrace:
    fallback_tracer = NoopTracer()

    def init_app(
        self,
        app,
        trace_extractor=None,
        tracer_generator=None,
        start_trace=None,
        end_trace=None,
        skip_index=True,
        trace_propagator=None,
        **kwargs,
    ):
        self.trace_propagator=trace_propagator
        @app.before_request
        def before_request():
            if skip_index and request.path == "/":
                return
            g.flask_trace_context["trace"] = trace_extractor()
            g.flask_trace_context["tracer"] = tracer_generator(g.trace)
            if start_trace:
                start_trace(g.flask_trace_context["tracer"])

        @app.after_request
        def after_request(response):
            if skip_index and request.path == "/":
                return response
            if end_trace:
                end_trace(g.flask_trace_context["tracer"])
            return response

    @property
    def tracer(self):
        if hasattr(g, "tracer"):
            return g.tracer
        return self.fallback_tracer

    @property
    def requests(self):
        if hasattr(g,"flask_trace_context"):
            header_name,header_value=self.trace_propagator(g.flask_trace_context["trace"],g.flask_trace_context["tracer"])
        
    
    def _requests(header_name,header_value):
