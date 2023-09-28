from csv import DictReader
from dataclasses import dataclass, field
from io import TextIOWrapper
from typing import Any, Dict, List
from zipfile import ZipFile

from gtfs.model import Service, ServiceChange, Stop, StopTime, Transfer, Trip
from gtfs.model.common import RecordBase


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
        'filename': 'transfers.txt',
        'fieldname': 'transfers',
        'class': Transfer
    }
]


@dataclass
class GTFS:
    stops: List[Stop]
    trips: List[Trip]
    stop_times: List[StopTime]

    services: List[Service] = field(default_factory=list)
    service_changes: List[ServiceChange] = field(default_factory=list)
    transfers: List[Transfer] = field(default_factory=list)


def read(path: str) -> GTFS:
    context: Dict[str, Any] = {}
    gtfs_fields: Dict[str, List[RecordBase]] = {}
    with ZipFile(path, 'r') as gtfs_file:
        for mapping in GTFS_DATASET_MAPPINGS:
            if mapping['filename'] not in gtfs_file.namelist():
                continue
            data = []
            with gtfs_file.open(mapping['filename'], 'r') as data_file:
                data_file_wrapper = TextIOWrapper(data_file, encoding='utf-8')
                reader = DictReader(data_file_wrapper)
                for row in reader:
                    data.append(mapping['class'](row, context))
            gtfs_fields[mapping['fieldname']] = data
    return GTFS(**gtfs_fields)  # type: ignore
