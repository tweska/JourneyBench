from .benchmark_core import Benchmark as BenchmarkCore
from .network import Network
from .queries import Queries


class Benchmark(BenchmarkCore):
    def __init__(self, network: Network, queries: Queries, algorithm: str):
        super().__init__()
        self.network = network
        self.queries = queries

        algorithm = algorithm.lower()
        shared_object_filename = f'algorithms/{algorithm}/{algorithm}.so'
        if super().set_algorithm(shared_object_filename) != 0:
            raise Exception(f"Could not load algorithm '{algorithm}' from shared object file '{shared_object_filename}'!")

    def set_algorithm(self, name: str) -> None:
        name = name.lower()
        filename = f"algorithms/{name}/{name}.so"
        status = super().set_algorithm(filename)
        if status != 0:
            raise Exception(f"Could not load algorithm '{name}' from shared object file '{filename}'!")

    def run_preprocessing(self):
        if super().run_preprocessing() != 0:
            raise Exception("Preprocessing failed!")
