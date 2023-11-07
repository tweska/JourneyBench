from gzip import open
from typing import Any, Dict, Optional

from .benchmark_core import Node, Conn, Path
from .benchmark_core import Network as CoreNetwork

from .network_pb2 import PBNetwork, PBNetworkNode, PBNetworkConn, PBNetworkPath


class Network(CoreNetwork):
    end: Optional[int]

    __node_id_map: Dict[Any, int] = {}
    __trip_id_map: Dict[Any, int] = {}

    def __init__(self, end: Optional[int] = None):
        super().__init__()
        self.end = end

    def read(self, filepath: str) -> None:
        pb_network: PBNetwork = PBNetwork()
        with open(filepath, 'rb') as file:
            pb_network.ParseFromString(file.read())

        [self.trips.append([]) for _ in range(pb_network.trip_count)]

        for pb_node in pb_network.nodes:
            self.nodes.append(Node(
                pb_node.latitude,
                pb_node.longitude,
            ))

        for pb_conn in pb_network.conns:
            self.conns.append(Conn(
                pb_conn.trip_id,
                pb_conn.from_node_id,
                pb_conn.to_node_id,
                pb_conn.departure_time,
                pb_conn.arrival_time,
            ))
            self.trips[pb_conn.trip_id].append(self.conns[-1])

        for pb_path in pb_network.paths:
            self.paths.append(Path(
                pb_path.from_node_id,
                pb_path.to_node_id,
                pb_path.duration,
            ))

    def write(self, filepath: str) -> None:
        pb_network: PBNetwork = PBNetwork()
        pb_network.trip_count = len(self.trips)

        for node_id, node in enumerate(self.nodes):
            pb_node: PBNetworkNode = pb_network.nodes.add()
            pb_node.latitude = node.latitude
            pb_node.longitude = node.longitude

        for conn in sorted(self.conns, key=lambda c: c.departure_time):
            pb_conn: PBNetworkConn = pb_network.conns.add()
            pb_conn.trip_id = conn.trip_id
            pb_conn.from_node_id = conn.from_node_id
            pb_conn.to_node_id = conn.to_node_id
            pb_conn.departure_time = conn.departure_time
            pb_conn.arrival_time = conn.arrival_time

        for path in sorted(self.paths, key=lambda p: p.from_node_id):
            pb_path: PBNetworkPath = pb_network.paths.add()
            pb_path.from_node_id = path.from_node_id
            pb_path.to_node_id = path.to_node_id
            pb_path.duration = path.duration

        serialized_data = pb_network.SerializeToString()
        with open(filepath, 'wb') as file:
            file.write(serialized_data)

    def add_node(
            self,
            ext_node_id: Any,
            latitude: float,
            longitude: float,
    ) -> int:
        if ext_node_id in self.__node_id_map:
            raise Exception(f"Node with ID '{ext_node_id}' is already registered!")

        node_id = len(self.nodes)
        new_node = Node(latitude, longitude)
        self.__node_id_map[ext_node_id] = node_id
        self.nodes.append(new_node)

        return node_id

    def add_conn(
            self,
            ext_trip_id: Any,
            ext_from_node_id: Any,
            ext_to_node_id: Any,
            departure_time: int,
            arrival_time: int,
    ) -> int:
        if ext_from_node_id not in self.__node_id_map:
            raise Exception(f"From node with ID '{ext_from_node_id}' is not registered!")
        if ext_to_node_id not in self.__node_id_map:
            raise Exception(f"To node with ID '{ext_to_node_id}' is not registered!")
        if departure_time < 0 or arrival_time > self.end:
            return -1
        if departure_time > arrival_time:
            raise Exception("Departure time cannot be later than arrival time!")

        if ext_trip_id not in self.__trip_id_map:
            self.trips.append([])
        trip_id = self.__trip_id_map.setdefault(ext_trip_id, len(self.__trip_id_map))
        from_node_id = self.__node_id_map[ext_from_node_id]
        to_node_id = self.__node_id_map[ext_to_node_id]

        new_conn = Conn(trip_id, from_node_id, to_node_id, departure_time, arrival_time)
        self.conns.append(new_conn)
        self.trips[trip_id].append(new_conn)

    def add_path(
            self,
            ext_from_node_id: Any,
            ext_to_node_id: Any,
            duration: int,
    ) -> int:
        if ext_from_node_id not in self.__node_id_map:
            raise Exception(f"From node with ID '{ext_from_node_id}' is not registered!")
        if ext_to_node_id not in self.__node_id_map:
            raise Exception(f"To node with ID '{ext_to_node_id}' is not registered!")
        if duration < 0:
            raise Exception("Path with negative duration cannot be registered!")

        from_node_id = self.__node_id_map[ext_from_node_id]
        to_node_id = self.__node_id_map[ext_to_node_id]

        for id, path in enumerate(self.paths):
            if path.from_node_id == from_node_id and path.to_node_id == to_node_id:
                path.duration = min(path.duration, duration)
                return id

        self.paths.append(Path(from_node_id, to_node_id, duration))
        return len(self.paths) - 1
