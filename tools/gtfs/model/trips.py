from dataclasses import dataclass
from typing import Any, Dict

from .common import RecordBase, get_id


@dataclass(eq=False)
class Trip(RecordBase):
    trip_id: int
    service_id: int

    def __init__(self, values: Dict[str, str], context: Dict[str, Any]):
        trip_id_map = context.setdefault('trip_id_map', {})
        service_id_map = context['service_id_map']
        self.trip_id = get_id(trip_id_map, values['trip_id'])
        self.service_id = service_id_map[values['service_id']]

    def primary(self) -> int:
        return self.trip_id
