from collections import defaultdict
from gzip import open
from typing import Dict, List

from .benchmark_core import LegType, JourneyLeg, Journey, QueryResult, PreprocessingResult

from .results_pb2 import PBResults, PBLegType


class Results:
    preprocessing_results: List[PreprocessingResult]
    query_results: Dict[int, List[QueryResult]]

    def __init__(self):
        self.preprocessing_results = []
        self.query_results = defaultdict(list)

    def read(self, filepath: str) -> None:
        pb_results: PBResults = PBResults()
        with open(filepath, 'rb') as file:
            pb_results.ParseFromString(file.read())

        for pb_preprocessing_result in pb_results.preprocessing:
            self.preprocessing_results.append(pb_preprocessing_result.runtime_ns)

        for pb_query_result in pb_results.queries:
            query_result = QueryResult(pb_query_result.runtime_ns)
            for pb_journey in pb_query_result.journeys:
                journey = Journey()
                for pb_leg in pb_journey.legs:
                    if pb_leg.type == PBLegType.CONN:
                        type = LegType.CONN
                    else:
                        assert(pb_leg.type == PBLegType.PATH)
                        type = LegType.PATH
                    leg = JourneyLeg(type)
                    for part in pb_leg.parts:
                        leg.add_part(part)
                    journey.add_leg(leg)
                query_result.add_journey(journey)
            self.add_query_result(pb_query_result.query_id, query_result)

    def write(self, filepath: str) -> None:
        pb_results: PBResults = PBResults()

        for preprocessing_result in self.preprocessing_results:
            pb_preprocessing_result = pb_results.preprocessing.add()
            pb_preprocessing_result.runtime_ns = preprocessing_result.runtime_ns

        for query_id, query_results in self.query_results.items():
            for query_result in query_results:
                pb_query_result = pb_results.queries.add()
                pb_query_result.query_id = query_id
                pb_query_result.runtime_ns = query_result.runtime_ns

                for journey in query_result.journeys:
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

    def add_preprocessing_result(self, preprocessing_result: PreprocessingResult):
        self.preprocessing_results.append(preprocessing_result)

    def add_query_result(self, query_id: int, query_result: QueryResult):
        self.query_results[query_id].append(query_result)
