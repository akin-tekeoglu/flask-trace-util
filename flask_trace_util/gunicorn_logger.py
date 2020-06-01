"""
Contains Gunicorn specific loggers
"""
import json
from gunicorn.glogging import Logger


class GunicornLogger(Logger):
    """Extended gunicorn acces logger

    Arguments:
        Logger {object} -- [GunicornLogger]
    """

    exclude_routes = ["/"]
    include_request_headers = True
    include_response_headers = True
    _log_format_pairs = {
        "remote_address": "%(h)s",
        "timestamp": "%(t)s",
        "message": "%(m)s",
        "path": "%(U)s",
        "query": "%(q)s",
        "status": "%(s)s",
        "response_size": "%(B)s",
        "referer": "%(f)s",
        "user_agent": "%(a)s",
        "request_time": "%(L)s",
    }

    def access(self, resp, req, environ, request_time):
        """
        Access log function
        """
        if req.path in self.exclude_routes:
            return
        log_format = self._log_format_pairs.copy()
        if self.include_request_headers:
            log_format["request_headers"] = {}
            for k in req.headers:
                log_format["request_headers"][k.lower()] = f"%({{{k.lower()}}}i)s"

        if self.include_response_headers:
            log_format["response_headers"] = {}
            for k in resp.headers:
                log_format["response_headers"][k.lower()] = f"%({{{k.lower()}}}o)s"
        if hasattr(self, "insert_custom_variables"):
            cvars = self.get_custom_variables(resp, req)
            for k, value in cvars.items():
                log_format[k.lower()] = f"%({{{k.lower()}}}e)s"
                environ[k.lower()] = value
        self.cfg.access_log_format = json.dumps(log_format)
        super().access(resp, req, environ, request_time)
