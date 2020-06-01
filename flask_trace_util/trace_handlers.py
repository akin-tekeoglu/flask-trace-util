"""
Contains common trace extractors and delegators
"""
from flask import request, g


def gcloud_trace_extractor(project_id):
    """Trace extractor for google cloud GKE

    Arguments:
        project_id {str} -- project id
    """

    def extractor():
        trace = request.headers.get("X-Cloud-Trace-Context")
        if not trace:
            return None
        return f"projects/{project_id}/traces/{trace.split('/')[0]}"

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
