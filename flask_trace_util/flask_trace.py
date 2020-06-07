"""Flask trace core module

"""
import logging
import requests
from flask import g, request


class NoopTracer:
    """Fallback tracer for local development
    """

    def __getattr__(self, item):
        return None


class Requests:
    """Proxy requests module for trace header propagation
    """

    def __init__(self, header_provider):
        self.header_provider = header_provider

    def _request(self, method):
        headers = self.header_provider()

        def __request(url, **kwargs):
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            for header_name, header_value in headers.items():
                kwargs["headers"][header_name] = header_value
            return requests.request(method, url, **kwargs)

        return __request

    def __getattr__(self, item):
        if item in ("get", "post", "put", "patch", "delete"):
            return self._request(item)
        return None


class FlaskTrace:
    """Main trace class for all core operations

    """

    fallback_tracer = NoopTracer()

    def __init__(
        self,
        trace_extractor=None,
        tracer_generator=None,
        start_trace=None,
        end_trace=None,
        skip_index=True,
        trace_propagator=None,
        init_logger=False,
        trace_log_propagator=None,
        formatter=None,
        trace_enabled=True,
    ):
        self.trace_enabled = trace_enabled
        self.trace_extractor = trace_extractor
        self.tracer_generator = tracer_generator
        self.start_trace = start_trace
        self.end_trace = end_trace
        self.skip_index = skip_index
        self.trace_propagator = trace_propagator
        self._requests = Requests(self._header_provider)
        if init_logger:
            self._init_logger(formatter, trace_log_propagator)

    def init_app(
        self,
        app,
        trace_extractor=None,
        tracer_generator=None,
        start_trace=None,
        end_trace=None,
        skip_index=True,
        trace_propagator=None,
        init_logger=False,
        trace_log_propagator=None,
        formatter=None,
        trace_enabled=True,
    ):
        self.trace_enabled = (
            trace_enabled if trace_enabled is not None else self.trace_enabled
        )
        self.trace_extractor = trace_extractor or self.trace_extractor
        self.tracer_generator = tracer_generator or self.tracer_generator
        self.start_trace = start_trace or self.start_trace
        self.end_trace = end_trace or self.end_trace
        self.skip_index = skip_index if skip_index is not None else self.skip_index
        self.trace_propagator = trace_propagator or self.trace_propagator
        self._requests = (
            Requests(self._header_provider) if self.trace_propagator else self._requests
        )
        if init_logger:
            self._init_logger(formatter, trace_log_propagator)
        self._init_app(app)

    def _init_app(self, app):
        @app.before_request
        def before_request():
            if not self.trace_enabled or (self.skip_index and request.path == "/"):
                return
            g.flask_trace_context["trace"] = self.trace_extractor()
            g.flask_trace_context["tracer"] = self.tracer_generator(g.trace)
            if self.start_trace:
                self.start_trace(g.flask_trace_context["tracer"])

        @app.after_request
        def after_request(response):
            if not self.trace_enabled or (self.skip_index and request.path == "/"):
                return response
            if self.end_trace:
                self.end_trace(g.flask_trace_context["tracer"])
            return response

    def _header_provider(self):
        header_name, header_value = self.trace_propagator(
            g.flask_trace_context["trace"], g.flask_trace_context["tracer"]
        )
        return {header_name: header_value}

    def _init_logger(self, formatter, trace_log_propagator):
        _ = self

        class _TraceFormatter(formatter):
            def add_fields(self, log_record, record, message_dict):
                super().add_fields(log_record, record, message_dict)
                if _.trace_enabled and hasattr(g, "trace_context"):
                    log_name, log_value = trace_log_propagator()
                    log_record[log_name] = log_value

        logger = logging.getLogger("flask_trace_json_logger")
        log_handler = logging.StreamHandler()
        formatter = _TraceFormatter()
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.setLevel(logging.DEBUG)

    @property
    def tracer(self):
        """Tracer instance which was created by tracer_generator function

        Returns:
            object: tracer object
        """
        if hasattr(g, "tracer") and self.trace_enabled:
            return g.tracer
        return self.fallback_tracer

    @property
    def requests(self):
        """Requests module with propagated trace header

        Returns:
            object: requests module
        """
        if (
            hasattr(g, "flask_trace_context")
            and "trace_propagator" in g.flask_trace_context
            and self.trace_enabled
        ):
            return self._requests
        return requests
