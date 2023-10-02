from dataclasses import dataclass, field
from datetime import datetime, timedelta
from gzip import open as gzip_open
from typing import Any, Dict, List, Optional

from .network_pb2 import PBNetwork, PBNetworkConn, PBNetworkPath, PBNetworkStop


@dataclass(eq=False)
class NetworkStop:
    station_id: int
    latitude: float
    longitude: float
    stop_id: Optional[int] = None


@dataclass(eq=False)
class NetworkConn:
    trip_id: int
    from_stop: NetworkStop
    to_stop: NetworkStop
    departure_time: int
    arrival_time: int


@dataclass(eq=False)
class NetworkPath:
    from_stop: NetworkStop
    to_stop: NetworkStop
    duration: int


@dataclass(eq=False)
class NetworkWriter:
    start: datetime
    end: datetime

    stops: List[NetworkStop] = field(default_factory=list)
    conns: List[NetworkConn] = field(default_factory=list)
    paths: List[NetworkPath] = field(default_factory=list)

    __stop_map: Dict[Any, NetworkStop] = field(default_factory=dict)
    __station_map: Dict[Any, int] = field(default_factory=dict)
    __station_count: int = 0
    __trip_map: Dict[Any, int] = field(default_factory=dict)

    def write(
            self,
            filepath: str,
            compress_copy: bool = False,
    ) -> None:
        pb_network: PBNetwork = PBNetwork()
        pb_network.station_count = self.station_count
        pb_network.trip_count = self.trip_count

        self.stops.sort(key=lambda s: s.station_id)
        for stop_id, stop in enumerate(self.stops):
            stop.stop_id = stop_id
            pb_stop: PBNetworkStop = pb_network.stops.add()
            pb_stop.station_id = stop.station_id
            pb_stop.latitude = stop.latitude
            pb_stop.longitude = stop.longitude

        self.conns.sort(key=lambda c: c.departure_time)
        for conn in self.conns:
            pb_conn: PBNetworkConn = pb_network.conns.add()
            pb_conn.trip_id = conn.trip_id
            pb_conn.from_stop_id = conn.from_stop.stop_id
            pb_conn.to_stop_id = conn.to_stop.stop_id
            pb_conn.departure_time = conn.departure_time
            pb_conn.arrival_time = conn.arrival_time

        self.paths.sort(key=lambda p: p.from_stop.stop_id)
        for path in self.paths:
            pb_path: PBNetworkPath = pb_network.paths.add()
            pb_path.from_stop_id = path.from_stop.stop_id
            pb_path.to_stop_id = path.to_stop.stop_id
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
                station = self.__station_map[station_id] = self.__station_count
                self.__station_count += 1
        else:
            station = self.__station_count
            self.__station_count += 1

        new_stop = NetworkStop(station, latitude, longitude)
        self.__stop_map[stop_id] = new_stop
        self.stops.append(new_stop)

    def add_conn(
            self,
            trip_id: Any,
            from_stop_id: Any,
            to_stop_id: Any,
            departure_time: datetime,
            arrival_time: datetime,
    ):
        if from_stop_id not in self.__stop_map:
            raise Exception(f"From stop with ID '{from_stop_id}' is not registered!")
        if to_stop_id not in self.__stop_map:
            raise Exception(f"To stop with ID '{to_stop_id}' is not registered!")
        if departure_time < self.start:
            return
        if departure_time > arrival_time:
            raise Exception("Departure time cannot be later than arrival time!")

        trip = self.__trip_map.setdefault(trip_id, len(self.__trip_map))
        from_stop = self.__stop_map[from_stop_id]
        to_stop = self.__stop_map[to_stop_id]
        departure = int((departure_time - self.start).total_seconds())
        arrival = int((arrival_time - self.start).total_seconds())

        self.conns.append(NetworkConn(
            trip,
            from_stop,
            to_stop,
            departure,
            arrival,
        ))

    def add_path(
            self,
            from_stop_id: Any,
            to_stop_id: Any,
            duration: timedelta,
    ) -> None:
        if from_stop_id not in self.__stop_map:
            raise Exception(f"From stop with ID '{from_stop_id}' is not registered!")
        if to_stop_id not in self.__stop_map:
            raise Exception(f"To stop with ID '{to_stop_id}' is not registered!")
        if duration < timedelta(seconds=0):
            raise Exception("Path with negative duration cannot be registered!")

        from_stop = self.__stop_map[from_stop_id]
        to_stop = self.__stop_map[to_stop_id]

        for path in self.paths:
            if path.from_stop == from_stop and path.to_stop == to_stop:
                raise Exception(f"Path from stop with ID '{from_stop_id}' to stop with ID '{to_stop_id}' is already "
                                f"registered!")

        self.paths.append(NetworkPath(from_stop, to_stop, int(duration.total_seconds())))

    @property
    def stop_count(self):
        return len(self.stops)

    @property
    def conn_count(self):
        return len(self.conns)

    @property
    def path_count(self):
        return len(self.paths)

    @property
    def station_count(self):
        return self.__station_count

    @property
    def trip_count(self):
        return len(self.__trip_map)
