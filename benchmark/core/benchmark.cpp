#include <pybind11/pybind11.h>

#include <iostream>
#include <string>
#include <dlfcn.h>

#include "algobase.h"
#include "network.h"

using namespace std;


class Benchmark {
public:
    Network *network;

    int set_algorithm(char *filepath) {
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

        return (algorithm_eat == NULL && algorithm_bic == NULL);
    }

    int run_preprocessing() {
        if (network == NULL || algorithm == NULL || (algorithm_eat == NULL && algorithm_bic == NULL)) { return -1; }
        return algorithm->init(network);
    }

    int run_query_eat(uint32_t from_stop_id, uint32_t to_stop_id, uint32_t departure_time) {
        if (algorithm_eat == NULL) { return -1; }
        return algorithm_eat->query_eat(from_stop_id, to_stop_id, departure_time);
    }

    int run_query_bic(uint32_t from_stop_id, uint32_t to_stop_id, uint32_t departure_time) {
        if (algorithm_bic == NULL) { return -1; }
        return algorithm_bic->query_bic(from_stop_id, to_stop_id, departure_time);
    }

private:
    AlgorithmBase *algorithm;
    AlgorithmEAT *algorithm_eat;
    AlgorithmBiC *algorithm_bic;
};


namespace py = pybind11;

PYBIND11_MODULE(benchmark, m) {
    py::class_<Benchmark>(m, "BenchmarkCore")
            .def(py::init<>())
            .def("set_algorithm", &Benchmark::set_algorithm)
            .def("run_preprocessing", &Benchmark::run_preprocessing)
            .def("run_query_eat", &Benchmark::run_query_eat)
            .def("run_query_bic", &Benchmark::run_query_bic)
            .def_readwrite("network", &Benchmark::network);
}
