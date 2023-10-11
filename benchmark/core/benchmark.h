#ifndef BENCHMARK_H
#define BENCHMARK_H

#include "algobase.h"
#include "network.h"
#include "queries.h"
#include "results.h"
#include "types.h"

class Benchmark {
public:
    Network *network;

    int set_algorithm(char *filepath);
    int run_preprocessing();
    QueryResult *run_single_eat_query(u32 from_stop_id, u32 to_stop_id, u32 departure_time);
    QueryResult *run_single_bic_query(u32 from_stop_id, u32 to_stop_id, u32 departure_time);

private:
    AlgorithmBase *algorithm;
    AlgorithmEAT *algorithm_eat;
    AlgorithmBiC *algorithm_bic;
};

#endif
