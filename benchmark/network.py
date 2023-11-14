from gzip import open
from typing import Any, Dict, Optional

from .benchmark_core import Network as CoreNetwork
from .network_pb2 import PBNetwork, PBNetworkNode, PBNetworkConn, PBNetworkPath


class Network(CoreNetwork):
    end: Optional[int]

    __node_id_map: Optional[Dict[Any, int]] = {}
    __trip_id_map: Optional[Dict[Any, int]] = {}

    def __init__(self, end: Optional[int] = None):
        super().__init__()
        self.end = end

    def read(self, filepath: str) -> None:
        pb_network: PBNetwork = PBNetwork()
        with open(filepath, 'rb') as file:
            pb_network.ParseFromString(file.read())

        [self.add_trip() for _ in range(pb_network.trip_count)]

        for node_id, pb_node in enumerate(pb_network.nodes):
            self.add_node(node_id,
                          pb_node.latitude, pb_node.longitude,
                          pb_node.stop)

        for pb_conn in pb_network.conns:
            self.add_conn(pb_conn.trip_id,
                          pb_conn.from_node_id, pb_conn.to_node_id,
                          pb_conn.departure_time, pb_conn.arrival_time)

        for pb_path in pb_network.paths:
            self.add_path(pb_path.node_a_id, pb_path.node_b_id,
                          pb_path.duration)

    def write(self, filepath: str) -> None:
        self.sort()

        pb_network: PBNetwork = PBNetwork()
        pb_network.trip_count = len(self.trips)

        for node in self.nodes:
            pb_node: PBNetworkNode = pb_network.nodes.add()
            pb_node.latitude = node.latitude
            pb_node.longitude = node.longitude
            pb_node.stop = node.stop

        for conn in self.conns:
            pb_conn: PBNetworkConn = pb_network.conns.add()
            pb_conn.trip_id = conn.trip_id
            pb_conn.from_node_id = conn.from_node_id
            pb_conn.to_node_id = conn.to_node_id
            pb_conn.departure_time = conn.departure_time
            pb_conn.arrival_time = conn.arrival_time

        for path in self.paths:
            pb_path: PBNetworkPath = pb_network.paths.add()
            pb_path.node_a_id = path.node_a_id
            pb_path.node_b_id = path.node_b_id
            pb_path.duration = path.duration

        serialized_data = pb_network.SerializeToString()
        with open(filepath, 'wb') as file:
            file.write(serialized_data)

    def add_node(
            self,
            ext_node_id: Any,
            latitude: float,
            longitude: float,
            stop: bool = False,
    ) -> int:
        if ext_node_id in self.__node_id_map:
            raise Exception(f"Node with ID '{ext_node_id}' is already registered!")

        node_id = super().add_node(latitude, longitude, stop)
        self.__node_id_map[ext_node_id] = node_id
        return node_id

    def add_conn(
            self,
            ext_trip_id: Any,
            ext_from_node_id: Any,
            ext_to_node_id: Any,
            departure_time: int,
            arrival_time: int,
    ) -> None:
        if ext_from_node_id not in self.__node_id_map:
            raise Exception(f"From node with ID '{ext_from_node_id}' is not registered!")
        if ext_to_node_id not in self.__node_id_map:
            raise Exception(f"To node with ID '{ext_to_node_id}' is not registered!")
        if departure_time < 0 or arrival_time > self.end:
            return
        if departure_time > arrival_time:
            raise Exception("Departure time cannot be later than arrival time!")

        if ext_trip_id not in self.__trip_id_map:
            self.__trip_id_map[ext_trip_id] = super().add_trip()

        trip_id = self.__trip_id_map[ext_trip_id]
        from_node_id = self.__node_id_map[ext_from_node_id]
        to_node_id = self.__node_id_map[ext_to_node_id]

        super().add_conn(trip_id, from_node_id, to_node_id, departure_time, arrival_time)

    def add_path(
            self,
            ext_node_a_id: Any,
            ext_node_b_id: Any,
            duration: int,
    ) -> None:
        if ext_node_a_id not in self.__node_id_map:
            raise Exception(f"Node A with ID '{ext_node_a_id}' is not registered!")
        if ext_node_b_id not in self.__node_id_map:
            raise Exception(f"Node B with ID '{ext_node_b_id}' is not registered!")
        if duration < 0:
            raise Exception("Path with negative duration cannot be registered!")

        node_a_id = self.__node_id_map[ext_node_a_id]
        node_b_id = self.__node_id_map[ext_node_b_id]

        super().add_path(node_a_id, node_b_id, duration)
