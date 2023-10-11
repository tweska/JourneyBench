from datetime import datetime, timedelta
from gzip import open as gzip_open
from typing import Any, Dict, Optional

from .benchmark_core import Stop, Conn, Path
from .benchmark_core import Network as CoreNetwork

from .network_pb2 import PBNetwork, PBNetworkConn, PBNetworkPath, PBNetworkStop


class Network(CoreNetwork):
    start: Optional[datetime]
    end: Optional[datetime]

    __stop_id_map: Dict[Any, int] = {}
    __trip_id_map: Dict[Any, int] = {}
    __station_id_map: Dict[Any, int] = {}

    def __init__(self, start: Optional[datetime] = None, end: Optional[datetime] = None):
        super().__init__()
        self.start, self.end = start, end

    def read(
            self,
            filepath: str,
    ) -> None:
        pb_network: PBNetwork = PBNetwork()
        if filepath.endswith('.gz'):
            with gzip_open(filepath, 'rb') as file:
                pb_network.ParseFromString(file.read())
        else:
            with open(filepath, 'rb') as file:
                pb_network.ParseFromString(file.read())

        [self.stations.append([]) for _ in range(pb_network.station_count)]
        [self.trips.append([]) for _ in range(pb_network.trip_count)]

        for stop_id, pb_stop in enumerate(pb_network.stops):
            self.stops.append(Stop(
                stop_id,
                pb_stop.station_id,
                pb_stop.latitude,
                pb_stop.longitude,
            ))
            self.stations[pb_stop.station_id].append(self.stops[-1])

        for pb_conn in pb_network.conns:
            self.conns.append(Conn(
                pb_conn.trip_id,
                pb_conn.from_stop_id,
                pb_conn.to_stop_id,
                pb_conn.departure_time,
                pb_conn.arrival_time,
            ))
            self.trips[pb_conn.trip_id].append(self.conns[-1])

        for pb_path in pb_network.paths:
            self.paths.append(Path(
                pb_path.from_stop_id,
                pb_path.to_stop_id,
                pb_path.duration,
            ))

    def write(
            self,
            filepath: str,
            compress_copy: bool = False,
    ) -> None:
        pb_network: PBNetwork = PBNetwork()
        pb_network.station_count = len(self.stations)
        pb_network.trip_count = len(self.trips)

        for stop_id, stop in enumerate(self.stops):
            assert(stop.stop_id == stop_id)
            pb_stop: PBNetworkStop = pb_network.stops.add()
            pb_stop.station_id = stop.station_id
            pb_stop.latitude = stop.latitude
            pb_stop.longitude = stop.longitude

        for conn in sorted(self.conns, key=lambda c: c.departure_time):
            pb_conn: PBNetworkConn = pb_network.conns.add()
            pb_conn.trip_id = conn.trip_id
            pb_conn.from_stop_id = conn.from_stop_id
            pb_conn.to_stop_id = conn.to_stop_id
            pb_conn.departure_time = conn.departure_time
            pb_conn.arrival_time = conn.arrival_time

        for path in sorted(self.paths, key=lambda p: p.from_stop_id):
            pb_path: PBNetworkPath = pb_network.paths.add()
            pb_path.from_stop_id = path.from_stop_id
            pb_path.to_stop_id = path.to_stop_id
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
            ext_stop_id: Any,
            latitude: float,
            longitude: float,
            ext_station_id: Any = None,
    ) -> None:
        if ext_stop_id in self.__stop_id_map:
            raise Exception(f"Stop with ID '{ext_stop_id}' is already registered!")

        stop_id = len(self.stops)

        if ext_station_id and ext_station_id in self.__station_id_map:
            station_id = self.__station_id_map[ext_station_id]
        else:
            station_id = len(self.stations)
            self.stations.append([])
            if ext_station_id:
                self.__stop_id_map[ext_station_id] = station_id

        new_stop = Stop(stop_id, station_id, latitude, longitude)
        self.__stop_id_map[ext_stop_id] = stop_id
        self.stops.append(new_stop)
        self.stations[station_id].append(new_stop)

    def add_conn(
            self,
            ext_trip_id: Any,
            ext_from_stop_id: Any,
            ext_to_stop_id: Any,
            departure_time: datetime,
            arrival_time: datetime,
    ):
        if ext_from_stop_id not in self.__stop_id_map:
            raise Exception(f"From stop with ID '{ext_from_stop_id}' is not registered!")
        if ext_to_stop_id not in self.__stop_id_map:
            raise Exception(f"To stop with ID '{ext_to_stop_id}' is not registered!")
        if departure_time < self.start or arrival_time > self.end:
            return
        if departure_time > arrival_time:
            raise Exception("Departure time cannot be later than arrival time!")

        if ext_trip_id not in self.__trip_id_map:
            self.trips.append([])
        trip_id = self.__trip_id_map.setdefault(ext_trip_id, len(self.__trip_id_map))
        from_stop_id = self.__stop_id_map[ext_from_stop_id]
        to_stop_id = self.__stop_id_map[ext_to_stop_id]
        departure = int((departure_time - self.start).total_seconds())
        arrival = int((arrival_time - self.start).total_seconds())

        new_conn = Conn(trip_id, from_stop_id, to_stop_id, departure, arrival)
        self.conns.append(new_conn)
        self.trips[trip_id].append(new_conn)

    def add_path(
            self,
            ext_from_stop_id: Any,
            ext_to_stop_id: Any,
            duration: timedelta,
    ) -> None:
        if ext_from_stop_id not in self.__stop_id_map:
            raise Exception(f"From stop with ID '{ext_from_stop_id}' is not registered!")
        if ext_to_stop_id not in self.__stop_id_map:
            raise Exception(f"To stop with ID '{ext_to_stop_id}' is not registered!")
        if duration < timedelta(seconds=0):
            raise Exception("Path with negative duration cannot be registered!")

        from_stop_id = self.__stop_id_map[ext_from_stop_id]
        to_stop_id = self.__stop_id_map[ext_to_stop_id]

        for path in self.paths:
            if path.from_stop_id == from_stop_id and path.to_stop_id == to_stop_id:
                raise Exception(f"Path from stop with ID '{ext_from_stop_id}' to stop with ID '{ext_to_stop_id}' is already "
                                f"registered!")

        self.paths.append(Path(from_stop_id, to_stop_id, int(duration.total_seconds())))
