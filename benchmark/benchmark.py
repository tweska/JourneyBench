from benchmark.journeybench_core import Benchmark as BenchmarkCore
from benchmark.network import Network


class Benchmark(BenchmarkCore):

    def set_algorithm(self, name: str) -> None:
        name = name.lower()
        filename = f"algorithms/{name}/{name}.so"
        status = super().set_algorithm(filename)
        if status != 0:
            raise Exception(f"Could not load algorithm '{name}' from shared object file '{filename}'!")

    def set_network(self, filepath: str) -> None:
        network = Network()
        network.read(filepath)
        self.network = network

    def run_preprocessing(self):
        if super().run_preprocessing() != 0:
            raise Exception("Preprocessing failed!")

    def run_query_eat(self, from_stop_id: int, to_stop_id: int, departure_time: int):
        if super().run_query_eat(from_stop_id, to_stop_id, departure_time) != 0:
            raise Exception(f"EAT query ({from_stop_id} -> {to_stop_id} @ {departure_time}) failed!")

    def run_query_bic(self, from_stop_id: int, to_stop_id: int, departure_time: int):
        if super().run_query_bic(from_stop_id, to_stop_id, departure_time) != 0:
            raise Exception(f"BiC query ({from_stop_id} -> {to_stop_id} @ {departure_time}) failed!")
