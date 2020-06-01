"""
Contains common trace extractors and delegators
"""


def gcloud_trace_extractor(project_id):
    """Trace extractor for google cloud GKE

    Arguments:
        project_id {str} -- project id
    """

    def extractor(request):
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

    def delegator(trace):
        header = trace.split("/")[-1]
        return "X-Cloud-Trace-Context", header

    return delegator
