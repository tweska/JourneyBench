from gzip import open
from typing import TypeVar

from .benchmark_core import Queries as CoreQueries
from .benchmark_core import Query as CoreQuery

from .queries_pb2 import PBQueries, PBQuery


Self = TypeVar("Self", bound="Queries")


class Query(CoreQuery):
    def __repr__(self):
        return (f"Query(from_node_id: {self.from_node_id}, to_node_id: {self.to_node_id}, "
                f"departure_time: {self.departure_time})")


class Queries(CoreQueries):

    def __repr__(self):
        return f"Queries(queries: {len(self.queries)})"

    @classmethod
    def read(cls, filepath: str) -> Self:
        queries = Queries()

        pb_queries: PBQueries = PBQueries()
        with open(filepath, 'rb') as file:
            pb_queries.ParseFromString(file.read())

        for pb_query in pb_queries.queries:
            queries.add_query(
                pb_query.from_node_id,
                pb_query.to_node_id,
                pb_query.departure_time,
            )

        return queries

    def write(self, filepath: str) -> None:
        pb_queries: PBQueries = PBQueries()

        for query in self.queries:
            pb_query: PBQuery = pb_queries.queries.add()
            pb_query.from_node_id = query.from_node_id
            pb_query.to_node_id = query.to_node_id
            pb_query.departure_time = query.departure_time

        with open(filepath, 'wb') as file:
            file.write(pb_queries.SerializeToString())

    def add_query(self, from_node_id: int, to_node_id: int, departure_time: int) -> int:
        return super().add_query(from_node_id, to_node_id, departure_time)
