"""
Contains common trace extractors and delegators
"""
from flask import request, g
from flask_trace_util.gunicorn_logger import GunicornLogger


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


class GCloudGunicornAccesLogger(GunicornLogger):
    """ Access logger for flask, gunicorn and google cloud

    Arguments:
        GunicornLogger {type} -- flask trace util GunicornLogger
    """

    project_id = None

    def get_custom_variables(self, resp, req):
        """Returns custom variables for acces logging

        Returns:
            dict -- custom env variables
        """
        trace = ""
        for k, value in req.headers:
            if k == "X-Cloud-Trace-Context":
                trace = f"projects/{self.project_id}/traces/{value.split('/')[0]}"
        return {"logging.googleapis.com/trace": trace}
