#ifndef NETWORK_FUNCTIONS_H
#define NETWORK_FUNCTIONS_H

#include "network.h"
#include "types.h"

u32 add_node(Network &network, f64 latitude, f64 longitude, bool stop);
u32 add_trip(Network &network);
void add_conn(Network &network, u32 trip_id, u32 from_node_id, u32 to_node_id, u32 departure_time, u32 arrival_time);
void add_path(Network &network, u32 node_a_id, u32 node_b_id, u32 duration);
void sort_network(Network &network);

#endif
