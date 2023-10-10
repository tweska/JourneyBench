#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include "network.h"
#include "types.h"

using namespace network;
namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(std::vector<Stop>);
PYBIND11_MAKE_OPAQUE(std::vector<Conn>);
PYBIND11_MAKE_OPAQUE(std::vector<Path>);
PYBIND11_MAKE_OPAQUE(std::vector<std::vector<Stop*>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::vector<Conn*>>);

PYBIND11_MODULE(network, m) {
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

    py::bind_vector<std::vector<Stop>>(m, "VectorStop");
    py::bind_vector<std::vector<Conn>>(m, "VectorConn");
    py::bind_vector<std::vector<Path>>(m, "VectorPath");
    py::bind_vector<std::vector<std::vector<Stop*>>>(m, "VectorStation");
    py::bind_vector<std::vector<std::vector<Conn*>>>(m, "VectorTrip");
}
