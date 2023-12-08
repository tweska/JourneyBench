from collections import defaultdict
from csv import DictReader
from dataclasses import dataclass, field
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Dict, List, TypeVar
from zipfile import ZipFile

from .model import Pathway, Service, ServiceChange, Stop, StopTime, Trip
from .model.common import RecordBase, RecordExistsException


GTFS_DATASET_MAPPINGS: List[Dict[str, Any]] = [
    {
        'filename': 'stops.txt',
        'fieldname': 'stops',
        'class': Stop
    },
    {
        'filename': 'calendar.txt',
        'fieldname': 'services',
        'class': Service
    },
    {
        'filename': 'calendar_dates.txt',
        'fieldname': 'service_changes',
        'class': ServiceChange
    },
    {
        'filename': 'trips.txt',
        'fieldname': 'trips',
        'class': Trip
    },
    {
        'filename': 'stop_times.txt',
        'fieldname': 'stop_times',
        'class': StopTime
    },
    {
        'filename': 'pathways.txt',
        'fieldname': 'pathways',
        'class': Pathway
    }
]

Self = TypeVar("Self", bound="GTFS")

@dataclass
class GTFS:
    stops: List[Stop]
    trips: List[Trip]
    stop_times: List[StopTime]

    services: List[Service] = field(default_factory=list)
    service_changes: List[ServiceChange] = field(default_factory=list)
    pathways: List[Pathway] = field(default_factory=list)

    def __repr__(self) -> str:
        return f'GTFS(stops: {len(self.stops)}, trips: {len(self.trips)}, stop_times: {len(self.stop_times)})'

    @classmethod
    def read(cls, paths: List[Path]) -> Self:
        context: Dict[str, Any] = {}
        gtfs_fields: Dict[str, List[RecordBase]] = defaultdict(list)

        for path in paths:
            with ZipFile(path, 'r') as gtfs_file:
                for mapping in GTFS_DATASET_MAPPINGS:
                    if mapping['filename'] not in gtfs_file.namelist():
                        continue
                    data = []
                    with gtfs_file.open(mapping['filename'], 'r') as data_file:
                        data_file_wrapper = TextIOWrapper(data_file, encoding='utf-8')
                        reader = DictReader(data_file_wrapper)
                        for row in reader:
                            try:
                                data.append(mapping['class'](row, context))
                            except RecordExistsException:
                                continue
                    gtfs_fields[mapping['fieldname']] += data

        return GTFS(**gtfs_fields)  # type: ignore
