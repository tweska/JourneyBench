from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Tuple

from .common import DATE_FORMAT, RecordBase, get_id


class SCExceptionType(Enum):
    ADDED = 1
    REMOVED = 2


@dataclass(eq=False)
class ServiceChange(RecordBase):
    service_id: int
    date: date
    exception_type: SCExceptionType

    def __init__(self, values: Dict[str, str], context: Dict[str, Any]):
        service_id_map = context.setdefault('service_id_map', {})
        self.service_id = get_id(service_id_map, values['service_id'])
        self.date = datetime.strptime(values['date'], DATE_FORMAT).date()
        if int(values['exception_type']) == 1:
            self.exception_type = SCExceptionType.ADDED
        else:
            self.exception_type = SCExceptionType.REMOVED

    def primary(self) -> Tuple[int, int]:
        return self.service_id, \
            int(datetime.combine(self.date, datetime.min.time()).timestamp())
