"""
Base module for flask_trace_util
"""
from .flask_trace import (
    _FlaskTrace,
    gcloud_trace_delegator,
    gcloud_trace_extractor,
    simple_user_id_extractor,
    simple_user_id_delegator,
)

gcloud_trace = _FlaskTrace(
    delegator=gcloud_trace_delegator,
    user_id_extractor=simple_user_id_extractor,
    user_id_delegator=simple_user_id_delegator,
)
