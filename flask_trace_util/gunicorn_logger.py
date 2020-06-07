"""
Contains Gunicorn specific loggers
"""
import json
from datetime import datetime
import traceback
from gunicorn.glogging import Logger
import requests


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
        "message": "%(r)s",
        "path": "%(U)s",
        "query": "%(q)s",
        "status": "%(s)s",
        "response_size": "%(B)s",
        "referer": "%(f)s",
        "user_agent": "%(a)s",
        "request_time": "%(L)s",
        "method": "%(m)s",
    }

    def get_custom_variables(self, resp, req):
        """Override this function to provide custom variable

        Arguments:
            resp {object} -- gunicorn resp
            req {object} -- gunicorn resp

        Returns:
            dict -- custom variables
        """
        return {}

    def access(self, resp, req, environ, request_time):
        """
        Access log function
        """
        if req.path in self.exclude_routes:
            return
        log_format = self._log_format_pairs.copy()
        if self.include_request_headers:
            log_format["request_headers"] = {}
            for k, _ in req.headers:
                log_format["request_headers"][k.lower()] = f"%({{{k.lower()}}}i)s"

        if self.include_response_headers:
            log_format["response_headers"] = {}
            for k, _ in resp.headers:
                log_format["response_headers"][k.lower()] = f"%({{{k.lower()}}}o)s"

        if hasattr(self, "get_custom_variables"):
            cvars = self.get_custom_variables(resp, req)
            for k, value in cvars.items():
                log_format[k.lower()] = f"%({{{k.lower()}}}e)s"
                environ[k.lower()] = value
        access_log_format = json.dumps(log_format)

        if not (
            self.cfg.accesslog
            or self.cfg.logconfig
            or self.cfg.logconfig_dict
            or (self.cfg.syslog and not self.cfg.disable_redirect_access_to_syslog)
        ):
            return
        atoms = self.atoms(resp, req, environ, request_time)
        atoms["t"] = str(datetime.utcnow())
        for k, value in atoms.items():
            if isinstance(value, str) and '"' in value:
                atoms[k] = value.replace('"', "'")
        safe_atoms = self.atoms_wrapper_class(atoms)

        try:
            self.access_log.info(access_log_format, safe_atoms)
        except:
            self.error(traceback.format_exc())


class GCloudGunicornAccesLogger(GunicornLogger):
    """ Access logger for flask, gunicorn and google cloud

    Arguments:
        GunicornLogger {type} -- flask trace util GunicornLogger
    """

    project_id = None

    def __init__(self, cfg):
        resp = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
        )
        self.project_id = resp.text
        super().__init__(cfg)

    def get_custom_variables(self, resp, req):
        """Returns custom variables for acces logging

        Returns:
            dict -- custom env variables
        """
        cvars = {}
        for k, value in req.headers:
            if k.lower() == "X-Cloud-Trace-Context".lower():
                trace = value.split("/")[0]
                cvars[
                    "logging.googleapis.com/trace"
                ] = f"projects/{self.project_id}/traces/{trace}"
        return cvars
