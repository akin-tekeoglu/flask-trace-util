"""
Base module for flask_trace_util
"""
from opencensus.common.transports.async_ import AsyncTransport
from opencensus.ext.stackdriver.trace_exporter import StackdriverExporter
from opencensus.trace.propagation.google_cloud_format import GoogleCloudFormatPropagator
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler
from flask import request
from .flask_trace import FlaskTrace
from .util import GcloudJsonFormatter, get_gcloud_project_id


propogator = GoogleCloudFormatPropagator()


def gcloud_trace_extractor():
    return request.headers.get("X-Cloud-Trace-Context")


exporter = None
try:
    exporter = StackdriverExporter()
except:
    pass


def gcloud_opencensus_tracer_generator(trace):
    span_context = propogator.from_header(trace)
    tracer = Tracer(
        exporter=exporter, span_context=span_context, sampler=AlwaysOnSampler()
    )
    return tracer


def opencensus_start_trace(tracer):
    tracer.start_span(name=request.url)


def opencensus_end_trace(tracer):
    tracer.finish()


def gcloud_opencensus_trace_propagator(trace, tracer):
    trace_header = propogator.to_header(tracer.span_context)
    return "X-Cloud-Trace-Context", trace_header


project_id = get_gcloud_project_id()


def gcloud_trace_log_propagator():
    header = request.headers.get("X-Cloud-Trace-Context")
    if header:
        trace = header.split("/")[0]
    return "trace", f"projects/{project_id}/traces/{trace}"


flask_trace = FlaskTrace(
    trace_extractor=gcloud_trace_extractor,
    tracer_generator=gcloud_opencensus_tracer_generator,
    start_trace=opencensus_start_trace,
    end_trace=opencensus_end_trace,
    trace_propagator=gcloud_opencensus_trace_propagator,
    init_logger=True,
    trace_log_propagator=gcloud_trace_log_propagator,
    formatter=GcloudJsonFormatter,
)
