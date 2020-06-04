"""
Base module for flask_trace_util
"""
from opencensus.common.transports.async_ import AsyncTransport
from opencensus.ext.stackdriver.trace_exporter import StackdriverExporter
from opencensus.trace.propagation.google_cloud_format import GoogleCloudFormatPropagator
from .flask_trace import (
    _FlaskTrace,
    user_id_extractor,
    user_id_delegator,
    opencencus_trace_extractor,
    opencencus_trace_delegator,
    trace_delegator,
    trace_extractor,
    trace_serializer,
    user_id_serializer,
    gcloud_trace_serializer,
    gcloud_trace_json_logger,
)


sde = StackdriverExporter()

uid = user_id_delegator()
otd = (
    opencencus_trace_delegator("X-Cloud-Trace-Context", GoogleCloudFormatPropagator()),
)
delegators = trace_delegator([uid, otd])
extractors = trace_extractor(
    [
        user_id_extractor(),
        opencencus_trace_extractor(
            sde, "X-Cloud-Trace-Context", GoogleCloudFormatPropagator()
        ),
    ]
)

gcloud_opencencus_trace = _FlaskTrace(extractor=extractors, delegator=delegators,)


def init_gcloud_flask_trace_json_logger():
    serializers = trace_serializer(
        [user_id_serializer(uid), gcloud_trace_serializer(otd)]
    )
    gcloud_trace_json_logger(serializers)()
