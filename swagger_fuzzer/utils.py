""" Various helpers
"""
import json
from datetime import datetime


class CustomJsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)
