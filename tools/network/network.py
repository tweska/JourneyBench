from dataclasses import dataclass, field
from datetime import datetime, timedelta
from gzip import open as gzip_open
from typing import Any, Dict, List, Optional

from .network_pb2 import PBNetwork, PBNetworkPath, PBNetworkStation, PBNetworkStop, PBNetworkStopTime, PBNetworkTrip


@dataclass(eq=False)
class NetworkStop:
    latitude: float
    longitude: float
    id: Optional[int] = None


@dataclass(eq=False)
class NetworkStation:
    stops: List[NetworkStop] = field(default_factory=list)


@dataclass(eq=False)
class NetworkStopTime:
    stop: NetworkStop
    arrival_time: int
    departure_time: int


@dataclass(eq=False)
class NetworkTrip:
    stop_times: List[NetworkStopTime]


@dataclass(eq=False)
class NetworkPath:
    from_stop: NetworkStop
    to_stop: NetworkStop
    duration: int


@dataclass(eq=False)
class NetworkWriter:
    start: datetime
    end: datetime

    stations: List[NetworkStation] = field(default_factory=list)
    trips: List[NetworkTrip] = field(default_factory=list)
    paths: List[NetworkPath] = field(default_factory=list)

    __stop_map: Dict[Any, NetworkStop] = field(default_factory=dict)
    __station_map: Dict[Any, NetworkStation] = field(default_factory=dict)

    @property
    def stops(self) -> List[NetworkStop]:
        return [stop for station in self.stations for stop in station.stops]

    def write(
            self,
            filepath: str,
            compress_copy: bool = False,
    ) -> None:
        stop_count = 0

        pb_network: PBNetwork = PBNetwork()

        for station in self.stations:
            pb_station: PBNetworkStation = pb_network.stations.add()
            for stop in station.stops:
                stop.id = stop_count
                stop_count += 1

                pb_stop: PBNetworkStop = pb_station.stops.add()
                pb_stop.latitude = stop.latitude
                pb_stop.longitude = stop.longitude

        for trip in self.trips:
            pb_trip: PBNetworkTrip = pb_network.trips.add()
            for stop_time in trip.stop_times:
                pb_stop_time: PBNetworkStopTime = pb_trip.stop_times.add()
                pb_stop_time.stop_id = stop_time.stop.id
                pb_stop_time.arrival_time = stop_time.arrival_time
                pb_stop_time.departure_time = stop_time.departure_time

        for path in self.paths:
            pb_path: PBNetworkPath = pb_network.paths.add()
            pb_path.from_stop_id = path.from_stop.id
            pb_path.to_stop_id = path.to_stop.id
            pb_path.duration = path.duration

        serialized_data = pb_network.SerializeToString()
        with open(filepath, 'wb') as file:
            file.write(serialized_data)

        if not compress_copy:
            return

        with gzip_open(f'{filepath}.gz', 'wb') as file:
            file.write(serialized_data)

    def add_stop(
            self,
            stop_id: Any,
            latitude: float,
            longitude: float,
            station_id: Any = None,
    ) -> None:
        if stop_id in self.__stop_map:
            raise Exception(f"Stop with ID '{stop_id}' is already registered!")

        if station_id:
            if station_id in self.__station_map:
                station = self.__station_map[station_id]
            else:
                self.__station_map[station_id] = station = NetworkStation()
                self.stations.append(station)
        else:
            station = NetworkStation()
            self.stations.append(station)

        new_stop = NetworkStop(latitude, longitude)
        self.__stop_map[stop_id] = new_stop
        station.stops.append(new_stop)

    def add_trip(
            self,
            stop_ids: List[Any],
            arrival_times: List[datetime],
            departure_times: List[datetime],
    ) -> None:
        if not (len(stop_ids) == len(arrival_times) == len(departure_times)):
            raise Exception("Number of stops, arrival times and departure times must be equal!")
        for stop_id in stop_ids:
            if stop_id not in self.__stop_map:
                raise Exception(f"Trip cannot be registered at unknown stop with ID '{stop_id}'!")

        stop_times = []
        for stop_id, arrival_time, departure_time in zip(stop_ids, arrival_times, departure_times):
            if arrival_time > self.end or departure_time < self.start:
                continue
            if arrival_time < self.start:
                arrival_time = departure_time
            if departure_time > self.end:
                departure_time = arrival_time

            stop_times.append(NetworkStopTime(
                self.__stop_map[stop_id],
                int((arrival_time - self.start).total_seconds()),
                int((departure_time - self.start).total_seconds()),
            ))
        if len(stop_times) < 2:
            return
        self.trips.append(NetworkTrip(stop_times))

    def add_path(
            self,
            from_stop_id: Any,
            to_stop_id: Any,
            duration: timedelta,
    ) -> None:
        if from_stop_id not in self.__stop_map:
            raise Exception(f"Path from stop with ID '{from_stop_id}' cannot be registered! Stop is not registered.")
        if to_stop_id not in self.__stop_map:
            raise Exception(f"Path to stop with ID '{to_stop_id}' cannot be registered! Stop is not yet registered.")
        if duration < timedelta(seconds=0):
            raise Exception("Path with negative duration cannot be registered!")

        from_stop, to_stop = self.__stop_map[from_stop_id], self.__stop_map[to_stop_id]
        for path in self.paths:
            if path.from_stop == from_stop and path.to_stop == to_stop:
                raise Exception(f"Path from stop with ID '{from_stop_id}' to stop with ID '{to_stop_id}' is already "
                                f"registered!")

        self.paths.append(NetworkPath(from_stop, to_stop, int(duration.total_seconds())))
