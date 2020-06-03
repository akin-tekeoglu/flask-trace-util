"""
Base module for flask_trace_util
"""
from .flask_trace import _FlaskTrace, gcloud_trace_delegator, gcloud_trace_extractor

flask_trace = _FlaskTrace()
