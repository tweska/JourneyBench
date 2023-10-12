#include <dlfcn.h>

#include <chrono>

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

PreprocessingResult *Benchmark::run_preprocessing() {
    if (network == nullptr || algorithm == nullptr || (algorithm_eat == nullptr && algorithm_bic == nullptr)) { return nullptr; }

    auto start = chrono::steady_clock::now();
    /* Call the algorithm's initialization method. */
    int status = algorithm->init(network);
    auto end = chrono::steady_clock::now();
    auto runtime_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();

    if (status != 0) { return nullptr; }
    return new PreprocessingResult(runtime_ns);
}

QueryResult *Benchmark::run_single_eat_query(u32 from_stop_id, u32 to_stop_id, u32 departure_time) {
    if (network == nullptr || algorithm_eat == nullptr) { return nullptr; }

    auto start = chrono::steady_clock::now();
    /* Call the algorithm's query method. */
    Journey *journey = algorithm_eat->query_eat(from_stop_id, to_stop_id, departure_time);
    auto end = chrono::steady_clock::now();
    auto runtime_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();

    auto result = new QueryResult(runtime_ns, QueryType::EAT);
    result->journeys.push_back(*journey);
    delete journey;
    return result;
}

QueryResult *Benchmark::run_single_bic_query(u32 from_stop_id, u32 to_stop_id, u32 departure_time) {
    if (network == nullptr || algorithm_bic == nullptr) { return nullptr; }

    auto start = chrono::steady_clock::now();
    /* Call the algorithm's query method. */
    vector<Journey> *journeys = algorithm_bic->query_bic(from_stop_id, to_stop_id, departure_time);
    auto end = chrono::steady_clock::now();
    auto runtime_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();

    auto result = new QueryResult(runtime_ns, QueryType::BIC);
    for (const Journey& journey : *journeys) {
        result->journeys.push_back(journey);
    }
    delete journeys;
    return result;
}
