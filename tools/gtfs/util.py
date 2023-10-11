import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

from .gtfs import GTFS
from .model.calendar_dates import SCExceptionType


def find_date_range(gtfs: GTFS) -> Tuple[datetime.date, datetime.date]:
    """
    Finds the first and last service date of the GTFS feed.
    """
    dates = []
    for gtfs_service in gtfs.services:
        dates.append(gtfs_service.start_date)
        dates.append(gtfs_service.end_date)
    for gtfs_service_change in gtfs.service_changes:
        dates.append(gtfs_service_change.date)
    return min(dates), max(dates)


def generate_date_service_dict(gtfs: GTFS) -> Dict[datetime.date, List[int]]:
    """
    Generate a dictionary with dates as keys and valid service id's as values.
    """
    date_service_dict = defaultdict(list)

    # Find the active dates for each service
    for gtfs_service in gtfs.services:
        date = gtfs_service.start_date
        while date <= gtfs_service.end_date:
            weekday = date.weekday()
            if (weekday == 0 and gtfs_service.monday) or \
               (weekday == 1 and gtfs_service.tuesday) or \
               (weekday == 2 and gtfs_service.wednesday) or \
               (weekday == 3 and gtfs_service.thursday) or \
               (weekday == 4 and gtfs_service.friday) or \
               (weekday == 5 and gtfs_service.saturday) or \
               (weekday == 6 and gtfs_service.sunday):
                date_service_dict[date].append(gtfs_service.service_id)
            date += datetime.timedelta(days=1)

    # add or remove special service days
    for gtfs_service_change in gtfs.service_changes:
        if gtfs_service_change.exception_type == SCExceptionType.ADDED:
            date_service_dict[gtfs_service_change.date].append(gtfs_service_change.service_id)
        elif gtfs_service_change.exception_type == SCExceptionType.REMOVED:
            date_service_dict[gtfs_service_change.date].remove(gtfs_service_change.service_id)

    return date_service_dict


def generate_date_trip_dict(gtfs: GTFS) -> Dict[datetime.date, List[int]]:
    """
    Generate a dictionary with dates as keys and valid trip id's as values.
    """
    service_trip_dict = defaultdict(list)
    for gtfs_trip in gtfs.trips:
        service_trip_dict[gtfs_trip.service_id].append(gtfs_trip.trip_id)

    date_trip_dict = defaultdict(list)
    for date, services in generate_date_service_dict(gtfs).items():
        for service in services:
            date_trip_dict[date].extend(service_trip_dict[service])
    return date_trip_dict


def generate_trip_stop_time_dict(gtfs: GTFS) -> Dict[int, List[int]]:
    """
    Generate a dictionary with trip id's as keys and lists of stop time indices as values.
    """
    trip_stop_time = defaultdict(list)
    for index, gtfs_stop_time in enumerate(gtfs.stop_times):
        trip_stop_time[gtfs_stop_time.trip_id].append(index)

    for stop_times in trip_stop_time.values():
        stop_times.sort(key=lambda i: gtfs.stop_times[i].stop_sequence)
    return trip_stop_time


def find_busiest_date(gtfs: GTFS) -> datetime.date:
    """
    Finds the busiest schedule date in the GTFS feed based on the number of stop times.
    """
    trip_stop_times_count: Dict[int, int] = defaultdict(int)
    for gtfs_stop_time in gtfs.stop_times:
        trip_stop_times_count[gtfs_stop_time.trip_id] += 1

    service_stop_times_count: Dict[int, int] = defaultdict(int)
    for gtfs_trip in gtfs.trips:
        service_stop_times_count[gtfs_trip.service_id] += trip_stop_times_count[gtfs_trip.trip_id]

    date_service_dict = generate_date_service_dict(gtfs)
    date_stop_times_count: Dict[datetime.date, int] = defaultdict(int)
    for date, services in date_service_dict.items():
        for service in services:
            date_stop_times_count[date] += service_stop_times_count[service]

    return max(date_stop_times_count, key=date_stop_times_count.get)
