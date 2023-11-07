from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from .common import RecordBase, get_id


@dataclass(eq=False)
class Stop(RecordBase):
    stop_id: int
    stop_lat: float
    stop_lon: float

    def __init__(self, values: Dict[str, str], context: Dict[str, Any]):
        stop_id_map = context.setdefault('stop_id_map', {})
        self.stop_id = get_id(stop_id_map, values['stop_id'])
        self.stop_lat = float(values['stop_lat'])
        self.stop_lon = float(values['stop_lon'])

    def primary(self) -> int:
        return self.stop_id
