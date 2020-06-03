"""
Common utilities for internal usage
"""


def extract_gcloud_trace(header, project_id):
    """
    Extract trace header from X-Cloud-Trace-Context
    """
    trace = ""
    if not header:
        trace = ""
    else:
        trace = f"projects/{project_id}/traces/{header.split('/')[0]}"
    return ("logging.googleapis.com/trace", trace)
