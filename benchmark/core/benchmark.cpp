#include <dlfcn.h>

#include <chrono>
#include <iostream>

#include "algorithm.h"
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
    return 0;
}

int Benchmark::set_network(Network *network) {
    this->network = network;
    return 0;
}

PreprocessingResult *Benchmark::run_preprocessing() {
    if (algorithm == nullptr || network == nullptr) { return nullptr; }

    auto start = chrono::steady_clock::now();
    /* Call the algorithm's initialization method. */
    int status = algorithm->init(network);
    auto end = chrono::steady_clock::now();
    auto runtime_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();

    if (status != 0) { return nullptr; }
    return new PreprocessingResult(runtime_ns);
}

QueryResult *Benchmark::run_query(u32 from_node_id, u32 to_node_id, u32 departure_time) {
    if (algorithm == nullptr || network == nullptr) { return nullptr; }

    auto start = chrono::steady_clock::now();
    /* Call the algorithm's query method. */
    vector<Journey> *journeys = algorithm->query(from_node_id, to_node_id, departure_time);
    auto end = chrono::steady_clock::now();
    auto runtime_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();

    auto result = new QueryResult(runtime_ns);
    result->journeys = *journeys;
    delete journeys;
    return result;
}
