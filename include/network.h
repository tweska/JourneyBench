#ifndef NETWORK_H
#define NETWORK_H

#include <vector>

#include "types.h"

using namespace std;

namespace JourneyBench {

    struct Node {
        f64 latitude;
        f64 longitude;
        bool stop;
    };

    struct Conn {
        u32 trip_id;
        u32 from_node_id;
        u32 to_node_id;
        u32 departure_time;
        u32 arrival_time;
    };

    struct Path {
        u32 node_a_id;
        u32 node_b_id;
        u32 duration;
    };

    struct Network {
        vector <Node> nodes;
        vector <Conn> conns;
        vector <Path> paths;

        vector <vector<Conn *>> trips;
    };
}

#endif
