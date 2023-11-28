#ifndef BENCHMARK_H
#define BENCHMARK_H

#include "algorithm.h"
#include "network.h"
#include "queries.h"
#include "results.h"
#include "types.h"

namespace JourneyBench {

    class Benchmark {
    public:
        int set_algorithm(char *filepath);

        int set_network(Network *network);

        PreprocessingResult *run_preprocessing();

        QueryResult *run_query(u32 from_node_id, u32 to_node_id, u32 departure_time);

    private:
        AlgorithmBase *algorithm;
        JourneyBench::Network *network;
    };

}

#endif
