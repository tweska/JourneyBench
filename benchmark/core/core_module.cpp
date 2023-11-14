#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include "benchmark.h"
#include "network.h"
//#include "queries.h"
//#include "results.h"
#include "types.h"

#include "network_functions.h"

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(std::vector<Node>);
PYBIND11_MAKE_OPAQUE(std::vector<Conn>);
PYBIND11_MAKE_OPAQUE(std::vector<Path>);
PYBIND11_MAKE_OPAQUE(std::vector<std::vector<Conn*>>);

//PYBIND11_MAKE_OPAQUE(std::vector<Query>);
//
//PYBIND11_MAKE_OPAQUE(std::vector<QueryResult>);
//PYBIND11_MAKE_OPAQUE(std::vector<Journey>);
//PYBIND11_MAKE_OPAQUE(std::vector<JourneyLeg>);
//PYBIND11_MAKE_OPAQUE(std::vector<u32>);

PYBIND11_MODULE(benchmark_core, m) {
    py::class_<Benchmark>(m, "Benchmark")
            .def(py::init<>())
            .def("set_algorithm", &Benchmark::set_algorithm)
            .def("run_preprocessing", &Benchmark::run_preprocessing)
            .def("run_single_eat_query", &Benchmark::run_single_eat_query)
            .def("run_single_bic_query", &Benchmark::run_single_bic_query)
            .def("supports_eat_query", &Benchmark::supports_eat_query)
            .def("supports_bic_query", &Benchmark::supports_bic_query)
            .def_readwrite("network", &Benchmark::network);

    py::class_<Node>(m, "Node")
            .def_readonly("latitude", &Node::latitude)
            .def_readonly("longitude", &Node::longitude)
            .def_readonly("stop", &Node::stop);

    py::class_<Conn>(m, "Conn")
            .def_readonly("trip_id", &Conn::trip_id)
            .def_readonly("from_node_id", &Conn::from_node_id)
            .def_readonly("to_node_id", &Conn::to_node_id)
            .def_readonly("departure_time", &Conn::departure_time)
            .def_readonly("arrival_time", &Conn::arrival_time);

    py::class_<Path>(m, "Path")
            .def_readonly("node_a_id", &Path::node_a_id)
            .def_readonly("node_b_id", &Path::node_b_id)
            .def_readonly("duration", &Path::duration);

    py::class_<Network>(m, "Network")
            .def(py::init<>())
            .def_readonly("nodes", &Network::nodes)
            .def_readonly("conns", &Network::conns)
            .def_readonly("paths", &Network::paths)
            .def_readonly("trips", &Network::trips)
            .def("add_node", [](Network &network,
                                f64 latitude, f64 longitude,
                                bool stop) {
                return add_node(network,
                                latitude, longitude,
                                stop);
            })
            .def("add_trip", [](Network &network) {
                return add_trip(network);
            })
            .def("add_conn", [](Network &network,
                                u32 trip_id,
                                u32 from_node_id, u32 to_node_id,
                                u32 departure_time, u32 arrival_time) {
                return add_conn(network,
                                trip_id,
                                from_node_id, to_node_id,
                                departure_time, arrival_time);
            })
            .def("add_path", [](Network &network,
                                u32 node_a_id, u32 node_b_id,
                                u32 duration) {
                return add_path(network,
                                node_a_id, node_b_id,
                                duration);
            })
            .def("sort", [](Network &network) {
                return sort_network(network);
            });

//    py::class_<Query>(m, "Query")
//            .def(py::init<u32, u32, u32>())
//            .def_readonly("from_node_id", &Query::from_node_id)
//            .def_readonly("to_node_id", &Query::to_node_id)
//            .def_readonly("departure_time", &Query::departure_time);
//
//    py::class_<Queries>(m, "Queries")
//            .def(py::init<>())
//            .def_readwrite("queries", &Queries::queries);
//
//    py::enum_<LegType>(m, "LegType")
//            .value("CONN", LegType::CONN)
//            .value("PATH", LegType::PATH)
//            .export_values();
//
//    py::class_<JourneyLeg>(m, "JourneyLeg")
//            .def(py::init<LegType>())
//            .def_readonly("type", &JourneyLeg::type)
//            .def_readwrite("parts", &JourneyLeg::parts);
//
//    py::class_<Journey>(m, "Journey")
//            .def(py::init<>())
//            .def_readwrite("legs", &Journey::legs);
//
//    py::enum_<QueryType>(m, "QueryType")
//            .value("EAT", QueryType::EAT)
//            .value("BIC", QueryType::BIC)
//            .export_values();
//
//    py::class_<QueryResult>(m, "QueryResult")
//            .def(py::init<u64, QueryType>())
//            .def_readonly("runtime_ns", &QueryResult::runtime_ns)
//            .def_readonly("type", &QueryResult::type)
//            .def_readwrite("journeys", &QueryResult::journeys);
//
//    py::class_<PreprocessingResult>(m, "PreprocessingResult")
//            .def(py::init<u64>())
//            .def_readonly("runtime_ns", &PreprocessingResult::runtime_ns);

    py::bind_vector<std::vector<Node>>(m, "VectorNode");
    py::bind_vector<std::vector<Conn>>(m, "VectorConn");
    py::bind_vector<std::vector<Path>>(m, "VectorPath");
    py::bind_vector<std::vector<std::vector<Conn*>>>(m, "VectorTrip");

//    py::bind_vector<std::vector<Query>>(m, "VectorQuery");
//
//    py::bind_vector<std::vector<QueryResult>>(m, "VectorQueryResult");
//    py::bind_vector<std::vector<Journey>>(m, "VectorJourney");
//    py::bind_vector<std::vector<JourneyLeg>>(m, "VectorJourneyLeg");
//    py::bind_vector<std::vector<u32>>(m, "Vector_u32");
}
