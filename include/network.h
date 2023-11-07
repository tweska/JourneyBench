#ifndef NETWORK_H
#define NETWORK_H

#include <vector>

#include "types.h"

using namespace std;

struct Node {
    f64 latitude;
    f64 longitude;

    Node(f64 latitude, f64 longitude)
        : latitude(latitude), longitude(longitude) {}
};

struct Conn {
    u32 trip_id;
    u32 from_node_id;
    u32 to_node_id;
    u32 departure_time;
    u32 arrival_time;

    Conn(u32 trip_id, u32 from_node_id, u32 to_node_id, u32 departure_time, u32 arrival_time)
    : trip_id(trip_id), from_node_id(from_node_id), to_node_id(to_node_id), departure_time(departure_time), arrival_time(arrival_time) {}
};

struct Path {
    u32 from_node_id;
    u32 to_node_id;
    u32 duration;

    Path(u32 from_node_id, u32 to_node_id, u32 duration)
        : from_node_id(from_node_id), to_node_id(to_node_id), duration(duration) {}
};

struct Network {
    vector<Node> nodes;
    vector<Conn> conns;
    vector<Path> paths;

    vector<vector<Conn*>> trips;
};

#endif
