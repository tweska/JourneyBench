from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .common import RecordBase


@dataclass(eq=False)
class Transfer(RecordBase):
    from_stop_id: int
    to_stop_id: int
    min_transfer_time: int

    def __init__(self, values: Dict[str, str], context: Dict[str, Any]):
        stop_id_map = context['stop_id_map']
        self.from_stop_id = stop_id_map[values['from_stop_id']]
        self.to_stop_id = stop_id_map[values['to_stop_id']]
        self.min_transfer_time = int(values['min_transfer_time'])

    def primary(self) -> Tuple[int, int]:
        return self.from_stop_id, self.to_stop_id
