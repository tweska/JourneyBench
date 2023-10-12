#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include "benchmark.h"
#include "network.h"
#include "queries.h"
#include "results.h"
#include "types.h"

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(std::vector<Stop>);
PYBIND11_MAKE_OPAQUE(std::vector<Conn>);
PYBIND11_MAKE_OPAQUE(std::vector<Path>);
PYBIND11_MAKE_OPAQUE(std::vector<std::vector<Stop*>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::vector<Conn*>>);

PYBIND11_MAKE_OPAQUE(std::vector<Query>);

PYBIND11_MAKE_OPAQUE(std::vector<QueryResult>);
PYBIND11_MAKE_OPAQUE(std::vector<Journey>);
PYBIND11_MAKE_OPAQUE(std::vector<JourneyLeg>);
PYBIND11_MAKE_OPAQUE(std::vector<u32>);

PYBIND11_MODULE(benchmark_core, m) {
    py::class_<Benchmark>(m, "Benchmark")
            .def(py::init<>())
            .def("set_algorithm", &Benchmark::set_algorithm)
            .def("run_preprocessing", &Benchmark::run_preprocessing)
            .def("run_single_eat_query", &Benchmark::run_single_eat_query)
            .def("run_single_bic_query", &Benchmark::run_single_bic_query)
            .def_readwrite("network", &Benchmark::network);

    py::class_<Stop>(m, "Stop")
            .def(py::init<u32, u32, f64, f64>())
            .def_readonly("stop_id", &Stop::stop_id)
            .def_readonly("station_id", &Stop::station_id)
            .def_readonly("latitude", &Stop::latitude)
            .def_readonly("longitude", &Stop::longitude);

    py::class_<Conn>(m, "Conn")
            .def(py::init<u32, u32, u32, u32, u32>())
            .def_readonly("trip_id", &Conn::trip_id)
            .def_readonly("from_stop_id", &Conn::from_stop_id)
            .def_readonly("to_stop_id", &Conn::to_stop_id)
            .def_readonly("departure_time", &Conn::departure_time)
            .def_readonly("arrival_time", &Conn::arrival_time);

    py::class_<Path>(m, "Path")
            .def(py::init<u32, u32, u32>())
            .def_readonly("from_stop_id", &Path::from_stop_id)
            .def_readonly("to_stop_id", &Path::to_stop_id)
            .def_readonly("duration", &Path::duration);

    py::class_<Network>(m, "Network")
            .def(py::init<>())
            .def_readwrite("stops", &Network::stops)
            .def_readwrite("conns", &Network::conns)
            .def_readwrite("paths", &Network::paths)
            .def_readwrite("stations", &Network::stations)
            .def_readwrite("trips", &Network::trips);

    py::class_<Query>(m, "Query")
            .def(py::init<u32, u32, u32>())
            .def_readonly("from_stop_id", &Query::from_stop_id)
            .def_readonly("to_stop_id", &Query::to_stop_id)
            .def_readonly("departure_time", &Query::departure_time);

    py::class_<Queries>(m, "Queries")
            .def(py::init<>())
            .def_readwrite("queries", &Queries::queries);

    py::enum_<LegType>(m, "LegType")
            .value("CONN", LegType::CONN)
            .value("PATH", LegType::PATH)
            .export_values();

    py::class_<JourneyLeg>(m, "JourneyLeg")
            .def(py::init<LegType>())
            .def_readonly("type", &JourneyLeg::type)
            .def_readwrite("parts", &JourneyLeg::parts);

    py::class_<Journey>(m, "Journey")
            .def(py::init<>())
            .def_readwrite("legs", &Journey::legs);

    py::class_<QueryResult>(m, "QueryResult")
            .def(py::init<u64>())
            .def_readonly("runtime_ns", &QueryResult::runtime_ns)
            .def_readwrite("journeys", &QueryResult::journeys);

    py::class_<PreprocessingResult>(m, "PreprocessingResult")
            .def(py::init<u64>())
            .def_readonly("runtime_ns", &PreprocessingResult::runtime_ns);

    py::bind_vector<std::vector<Stop>>(m, "VectorStop");
    py::bind_vector<std::vector<Conn>>(m, "VectorConn");
    py::bind_vector<std::vector<Path>>(m, "VectorPath");
    py::bind_vector<std::vector<std::vector<Stop*>>>(m, "VectorStation");
    py::bind_vector<std::vector<std::vector<Conn*>>>(m, "VectorTrip");

    py::bind_vector<std::vector<Query>>(m, "VectorQuery");

    py::bind_vector<std::vector<QueryResult>>(m, "VectorQueryResult");
    py::bind_vector<std::vector<Journey>>(m, "VectorJourney");
    py::bind_vector<std::vector<JourneyLeg>>(m, "VectorJourneyLeg");
    py::bind_vector<std::vector<u32>>(m, "Vector_u32");
}
