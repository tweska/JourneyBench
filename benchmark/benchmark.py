from .benchmark_core import Benchmark as BenchmarkCore
from .network import Network
from .queries import Queries
from .results import Results


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

    def run_benchmark(self):
        results = Results()

        # Run the preprocessing for the algorithm.
        preprocessing_result = self.run_preprocessing()
        if not preprocessing_result:
            raise Exception("Preprocessing failed!")
        results.add_preprocessing_result(preprocessing_result)

        # Run each query once with the available query functions.
        for query_id, query in enumerate(self.queries.queries):
            if self.supports_eat_query():
                query_result = self.run_single_eat_query(
                    query.from_stop_id, query.to_stop_id, query.departure_time)
                results.add_query_result(query_id, query_result)
            if self.supports_bic_query():
                query_result = self.run_single_bic_query(
                    query.from_stop_id, query.to_stop_id, query.departure_time)
                results.add_query_result(query_id, query_result)

        return results
