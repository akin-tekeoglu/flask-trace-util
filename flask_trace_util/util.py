from pythonjsonlogger import jsonlogger
import requests


class GcloudJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(self, *args, **kwargs):
        kwargs["timestamp"] = True
        super().__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if log_record.get("level"):
            log_record["severity"] = log_record["level"].upper()
        else:
            log_record["severity"] = record.levelname


def get_gcloud_project_id():
    r = requests.get(
        "http://metadata.google.internal/computeMetadata/v1/project/project-id",
        headers={"Metadata-Flavor": "Google"},
    )
    if r.status_code > 399:
        return "PROJECT_ID_NOT_FOUND"
    return r.text
