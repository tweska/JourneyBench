from .benchmark_core import Benchmark as BenchmarkCore
from .network import Network
from .queries import Queries
from .results import Results


class Benchmark(BenchmarkCore):
    def __init__(self, network: Network, queries: Queries, algorithm: str):
        super().__init__()

        super().set_network(network)
        self.queries = queries

        algorithm = algorithm.lower()
        shared_object_filename = f'algorithms/{algorithm}/{algorithm}.so'
        if super().set_algorithm(shared_object_filename) != 0:
            raise Exception(f"Could not load algorithm '{algorithm}' from shared object file '{shared_object_filename}'!")

    def run_benchmark(self) -> Results:
        results = Results()

        # Run the preprocessing for the algorithm.
        preprocessing_result = self.run_preprocessing()
        if not preprocessing_result:
            raise Exception("Preprocessing failed!")
        results.add_preprocessing_result(preprocessing_result)

        # Run each query once with the available query functions.
        for query_id, query in enumerate(self.queries.queries):
            query_result = self.run_query(query.from_node_id, query.to_node_id, query.departure_time)
            results.add_query_result(query_id, query_result)

        return results
