#ifndef BENCHMARK_H
#define BENCHMARK_H

#include "algobase.h"
#include "network.h"
#include "types.h"

class Benchmark {
public:
    Network *network;

    int set_algorithm(char *filepath);
    int run_preprocessing();
    int run_query_eat(u32 from_stop_id, u32 to_stop_id, u32 departure_time);
    int run_query_bic(u32 from_stop_id, u32 to_stop_id, u32 departure_time);

private:
    AlgorithmBase *algorithm;
    AlgorithmEAT *algorithm_eat;
    AlgorithmBiC *algorithm_bic;
};

#endif
