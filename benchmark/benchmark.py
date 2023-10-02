import os
import gzip
import shutil

from core.benchmark import BenchmarkCore


class Benchmark(BenchmarkCore):

    def set_algorithm(self, name: str) -> None:
        filename = f"../algorithms/{name}/{name}.so"
        status = super().set_algorithm(filename)
        if status != 0:
            raise Exception(f"Could not load algorithm '{name}' from shared object file '{filename}'!")

    def set_network(self, org_filepath: str) -> None:
        if not org_filepath.endswith('.gz'):
            filepath = org_filepath
        else:
            filepath = f'/tmp/{os.path.splitext(os.path.basename(org_filepath))[0]}'
            with gzip.open(org_filepath, 'rb') as compressed_file, open(filepath, 'wb') as uncompressed_file:
                shutil.copyfileobj(compressed_file, uncompressed_file)

        status = super().set_network(filepath)
        if status != 0:
            raise Exception(f"Could not load network from network file '{filepath}'!")

    def run_preprocessing(self):
        if super().run_preprocessing() != 0:
            raise Exception("Preprocessing failed!")

    def run_query_eat(self, from_stop_id: int, to_stop_id: int, departure_time: int):
        if super().run_query_eat(from_stop_id, to_stop_id, departure_time) != 0:
            raise Exception(f"EAT query ({from_stop_id} -> {to_stop_id} @ {departure_time}) failed!")

    def run_query_bic(self, from_stop_id: int, to_stop_id: int, departure_time: int):
        if super().run_query_bic(from_stop_id, to_stop_id, departure_time) != 0:
            raise Exception(f"BiC query ({from_stop_id} -> {to_stop_id} @ {departure_time}) failed!")
