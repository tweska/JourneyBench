#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include "benchmark.h"
#include "network.h"
#include "queries.h"
//#include "results.h"
#include "types.h"

struct {
    bool operator()(Conn a, Conn b) const {
        return a.departure_time < b.departure_time;
    }
} connLess;

struct {
    bool operator()(Path a, Path b) const {
        return a.node_a_id < b.node_a_id or (a.node_a_id == b.node_a_id and a.node_b_id < b.node_b_id);
    }
} pathLess;

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(std::vector<Node>);
PYBIND11_MAKE_OPAQUE(std::vector<Conn>);
PYBIND11_MAKE_OPAQUE(std::vector<Path>);
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
            .def("set_network", &Benchmark::set_network)
            .def("run_preprocessing", &Benchmark::run_preprocessing)
            .def("run_query", &Benchmark::run_query);

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
            .def("add_node", [](Network &network, f64 latitude, f64 longitude, bool stop) {
                network.nodes.push_back({latitude, longitude, stop});
                return network.nodes.size() - 1;
            })
            .def("add_trip", [](Network &network) {
                network.trips.push_back({});
                return network.trips.size() - 1;
            })
            .def("add_conn", [](Network &network, u32 trip_id, u32 from_node_id, u32 to_node_id, u32 departure_time, u32 arrival_time) {
                network.conns.push_back({trip_id, from_node_id, to_node_id, departure_time, arrival_time});
            })
            .def("add_path", [](Network &network, u32 node_a_id, u32 node_b_id, u32 duration) {
                network.paths.push_back({node_a_id, node_b_id, duration});
            })
            .def("sort", [](Network &network) {
                std::sort(network.conns.begin(), network.conns.end(), connLess);
                std::sort(network.paths.begin(), network.paths.end(), pathLess);
            });

    py::class_<Query>(m, "Query")
            .def_readonly("from_node_id", &Query::from_node_id)
            .def_readonly("to_node_id", &Query::to_node_id)
            .def_readonly("departure_time", &Query::departure_time);

    py::class_<Queries>(m, "Queries")
            .def(py::init<>())
            .def_readonly("queries", &Queries::queries)
            .def("add_query", [](Queries &queries, u32 from_node_id, u32 to_node_id, u32 departure_time) {
                queries.queries.push_back({from_node_id, to_node_id, departure_time});
                return queries.queries.size() - 1;
            });

    py::enum_<LegType>(m, "LegType")
            .value("CONN", LegType::CONN)
            .value("PATH", LegType::PATH)
            .export_values();

    py::class_<JourneyLeg>(m, "JourneyLeg")
            .def(py::init<LegType>())
            .def_readonly("type", &JourneyLeg::type)
            .def_readonly("parts", &JourneyLeg::parts)
            .def("add_part", [](JourneyLeg &leg, u32 part) {
                leg.parts.push_back(part);
            });

    py::class_<Journey>(m, "Journey")
            .def(py::init<>())
            .def_readonly("legs", &Journey::legs)
            .def("add_leg", [](Journey &journey, JourneyLeg &leg) {
                journey.legs.push_back(leg);
            });

    py::class_<QueryResult>(m, "QueryResult")
            .def(py::init<u64>())
            .def_readonly("runtime_ns", &QueryResult::runtime_ns)
            .def_readonly("journeys", &QueryResult::journeys)
            .def("add_journey", [](QueryResult &result, Journey &journey) {
                result.journeys.push_back(journey);
            });

    py::class_<PreprocessingResult>(m, "PreprocessingResult")
            .def_readonly("runtime_ns", &PreprocessingResult::runtime_ns);

    py::bind_vector<std::vector<Node>>(m, "VectorNode");
    py::bind_vector<std::vector<Conn>>(m, "VectorConn");
    py::bind_vector<std::vector<Path>>(m, "VectorPath");
    py::bind_vector<std::vector<std::vector<Conn*>>>(m, "VectorTrip");

    py::bind_vector<std::vector<Query>>(m, "VectorQuery");

    py::bind_vector<std::vector<QueryResult>>(m, "VectorQueryResult");
    py::bind_vector<std::vector<Journey>>(m, "VectorJourney");
    py::bind_vector<std::vector<JourneyLeg>>(m, "VectorJourneyLeg");
    py::bind_vector<std::vector<u32>>(m, "Vector_u32");
}
