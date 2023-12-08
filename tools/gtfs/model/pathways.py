from dataclasses import dataclass
from typing import Any, Dict, Optional

from .common import RecordBase, RecordExistsException, get_id

@dataclass(eq=False)
class Pathway(RecordBase):
    pathway_id: int
    from_stop_id: int
    to_stop_id: int
    length: Optional[float]
    traversal_time: Optional[int]

    def __init__(self, values: Dict[str, str], context: Dict[str, Any]):
        pathway_id_map = context.setdefault('pathway_id_map', {})
        stop_id_map = context['stop_id_map']
        if values['pathway_id'] in pathway_id_map:
            raise RecordExistsException()
        self.pathway_id = get_id(pathway_id_map, values['pathway_id'])
        self.from_stop_id = stop_id_map[values['from_stop_id']]
        self.to_stop_id = stop_id_map[values['to_stop_id']]
        self.length = float(values['length']) if 'length' in values and values['length'] != '' else None
        self.traversal_time = int(values['traversal_time']) if 'traversal_time' in values and values['traversal_time'] != '' else None

    def primary(self) -> int:
        return self.pathway_id
