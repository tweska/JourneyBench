#include <iostream>
#include <string>
#include <dlfcn.h>

#include "algobase.h"
#include "network.h"
#include "types.h"

#include "benchmark.h"

using namespace std;

int Benchmark::set_algorithm(char *filepath) {
    /* Load the shared object file corresponding to the algorithm. */
    void *algorithmHandle = dlopen(filepath, RTLD_NOW);
    if (!algorithmHandle) { return -1; }

    /* Find the `createInstance` function. */
    using CreateFn = AlgorithmBase* (*)();
    CreateFn create = reinterpret_cast<CreateFn>(dlsym(algorithmHandle, "createInstance"));
    if (!create) { return -1; }

    /* Create an instance of the AlgorithmBase class implementation. */
    algorithm = create();
    algorithm_eat = dynamic_cast<AlgorithmEAT*>(algorithm);
    algorithm_bic = dynamic_cast<AlgorithmBiC*>(algorithm);

    return (algorithm_eat == nullptr && algorithm_bic == nullptr);
}

int Benchmark::run_preprocessing() {
    if (network == nullptr || algorithm == nullptr || (algorithm_eat == nullptr && algorithm_bic == nullptr)) { return -1; }
    /* TODO: Add timing code! */
    return algorithm->init(network);
}

QueryResult *Benchmark::run_single_eat_query(u32 from_stop_id, u32 to_stop_id, u32 departure_time) {
    if (network == nullptr || algorithm_eat == nullptr) { return NULL; }
    /* TODO: Add timing code! */
    Journey *journey = algorithm_eat->query_eat(from_stop_id, to_stop_id, departure_time);
    QueryResult *result = new QueryResult(0.0);
    result->journeys.push_back(*journey);
    delete journey;
    return result;
}

//int Benchmark::run_query_bic(u32 from_stop_id, u32 to_stop_id, u32 departure_time, Journey *result) {
//    if (algorithm_bic == nullptr || result == nullptr) { return -1; }
//    return algorithm_bic->query_bic(from_stop_id, to_stop_id, departure_time, result);
//}
