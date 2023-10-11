from gzip import open

from .benchmark_core import Queries as CoreQueries
from .benchmark_core import Query

from .queries_pb2 import PBQueries, PBQuery


class Queries(CoreQueries):
    def read(self, filepath: str) -> None:
        pb_queries: PBQueries = PBQueries()
        with open(filepath, 'rb') as file:
            pb_queries.ParseFromString(file.read())

        for pb_query in pb_queries.queries:
            self.queries.append(Query(
                pb_query.from_stop_id,
                pb_query.to_stop_id,
                pb_query.departure_time,
            ))

    def write(self, filepath: str) -> None:
        pb_queries: PBQueries = PBQueries()

        for query in self.queries:
            pb_query: PBQuery = pb_queries.queries.add()
            pb_query.from_stop_id = query.from_stop_id
            pb_query.to_stop_id = query.to_stop_id
            pb_query.departure_time = query.departure_time

        with open(filepath, 'wb') as file:
            file.write(pb_queries.SerializeToString())

    def add_query(self, from_stop_id: int, to_stop_id: int, departure_time: int) -> None:
        self.queries.append(Query(from_stop_id, to_stop_id, departure_time))
