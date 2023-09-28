from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

from .common import RecordBase, str2timedelta


@dataclass(eq=False)
class StopTime(RecordBase):
    trip_id: int
    stop_sequence: int
    stop_id: int
    arrival_time: Optional[timedelta]
    departure_time: Optional[timedelta]

    def __init__(self, values: Dict[str, str], context: Dict[str, Any]):
        trip_id_map = context['trip_id_map']
        stop_id_map = context['stop_id_map']
        self.trip_id = trip_id_map[values['trip_id']]
        self.stop_sequence = int(values['stop_sequence'])
        self.stop_id = stop_id_map[values['stop_id']]
        self.arrival_time = str2timedelta(values['arrival_time'])
        self.departure_time = str2timedelta(values['departure_time'])

    def primary(self) -> Tuple[int, int]:
        return self.trip_id, self.stop_sequence
