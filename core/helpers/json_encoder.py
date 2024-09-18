import json
from datetime import datetime
from uuid import UUID


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert to ISO 8601 format
        
        return super().default(obj)