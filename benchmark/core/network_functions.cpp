#include <algorithm>

#include "network.h"
#include "types.h"

#include "network_functions.h"

u32 add_node(Network &network,
             f64 latitude, f64 longitude,
             bool stop) {
    network.nodes.push_back({
        latitude, longitude,
        stop
    });
    return network.nodes.size() - 1;
}

u32 add_trip(Network &network) {
    network.trips.push_back({});
    return network.trips.size() - 1;
    return 0;
}

void add_conn(Network &network,
             u32 trip_id,
             u32 from_node_id, u32 to_node_id,
             u32 departure_time, u32 arrival_time) {
    network.conns.push_back({trip_id,
                             from_node_id, to_node_id,
                             departure_time, arrival_time});
}

void add_path(Network &network,
             u32 node_a_id, u32 node_b_id,
             u32 duration) {
    if (node_a_id > node_b_id) { return add_path(network, node_b_id, node_a_id, duration); }
    network.paths.push_back({
        node_a_id, node_b_id,
        duration
    });
}

struct {
    bool operator()(Conn a, Conn b) const { return a.departure_time < b.departure_time; }
} connLess;

struct {
    bool operator()(Path a, Path b) const { return a.node_a_id < b.node_a_id or
        (a.node_a_id == b.node_a_id and a.node_b_id < b.node_b_id); }
} pathLess;

void sort_network(Network &network) {
    std::sort(network.conns.begin(), network.conns.end(), connLess);
    std::sort(network.paths.begin(), network.paths.end(), pathLess);
}
