#ifndef NETWORK_H
#define NETWORK_H

#include <cstdint>

struct Network;
struct NetworkStop;
struct NetworkConn;
struct NetworkPath;

struct Network {
    uint32_t stop_count;
    uint32_t conn_count;
    uint32_t path_count;

    uint32_t station_count;
    uint32_t trip_count;

    NetworkStop *stops;
    NetworkConn *conns;
    NetworkPath *paths;

    NetworkStop **stations;
    NetworkConn **trips;
};

struct NetworkStop {
    uint32_t stop_id;
    uint32_t station_id;
    double latitude;
    double longitude;

    NetworkStop *next_in_station;
};

struct NetworkConn {
    uint32_t trip_id;
    uint32_t from_stop_id;
    uint32_t to_stop_id;
    uint32_t departure_time;
    uint32_t arrival_time;

    NetworkConn *next_in_trip;
};

struct NetworkPath {
    uint32_t from_stop_id;
    uint32_t to_stop_id;
    uint32_t duration;
};

#endif
