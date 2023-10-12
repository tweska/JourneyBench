from gzip import open

from .benchmark_core import LegType, JourneyLeg, Journey, QueryResult, QueryType

from .results_pb2 import PBResults, PBLegType, PBQueryType


class Results:
    preprocessing_results = []
    query_results = []

    def read(self, filepath: str) -> None:
        pb_results: PBResults = PBResults()
        with open(filepath, 'rb') as file:
            pb_results.ParseFromString(file.read())

        for pb_preprocessing_result in pb_results.preprocessing:
            self.preprocessing_results.append(pb_preprocessing_result.runtime_ns)

        for pb_query_result in pb_results.queries:
            if pb_query_result.type == PBQueryType.EAT:
                type = QueryType.EAT
            else:
                assert(pb_query_result.type == PBQueryType.BIC)
                type = QueryType.BIC
            self.query_results.append((pb_query_result.query_id, QueryResult(pb_query_result.runtime_ns, type)))
            for pb_journey in pb_query_result.journeys:
                self.query_results[-1][1].journeys.append(Journey())
                for pb_leg in pb_journey.legs:
                    if pb_leg.type == PBLegType.CONN:
                        type = LegType.CONN
                    else:
                        assert(pb_leg.type == PBLegType.PATH)
                        type = LegType.PATH
                    self.query_results[-1][1].journeys[-1].legs.append(JourneyLeg(type))
                    for part in pb_leg.parts:
                        self.query_results[-1][1].journeys[-1].legs[-1].parts.append(part)

    def write(self, filepath: str) -> None:
        pb_results: PBResults = PBResults()

        for preprocessing_result in self.preprocessing_results:
            pb_preprocessing_result = pb_results.preprocessing.add()
            pb_preprocessing_result.runtime_ns = preprocessing_result.runtime_ns

        for query_result in self.query_results:
            pb_query_result = pb_results.queries.add()
            pb_query_result.query_id = query_result[0]
            pb_query_result.runtime_ns = query_result[1].runtime_ns
            if query_result[1].type == QueryType.EAT:
                pb_query_result.type = PBQueryType.EAT
            else:
                assert(query_result[1].type == QueryType.BIC)
                pb_query_result.type = PBQueryType.BIC

            for journey in query_result[1].journeys:
                pb_journey = pb_query_result.journeys.add()
                for leg in journey.legs:
                    pb_leg = pb_journey.legs.add()
                    if leg.type == LegType.CONN:
                        pb_leg.type = PBLegType.CONN
                    else:
                        assert(leg.type == LegType.PATH)
                        pb_leg.type = PBLegType.PATH
                    for part in leg.parts:
                        pb_leg.parts.append(part)

        with open(filepath, 'wb') as file:
            file.write(pb_results.SerializeToString())

    def add_preprocessing_result(self, runtime_ns: int):
        self.preprocessing_results.append(runtime_ns)

    def add_query_result(self, query_id: int, query_result: QueryResult):
        self.query_results.append((query_id, query_result))
