#ifndef NETWORK_H
#define NETWORK_H

#include <vector>

#include "types.h"

using namespace std;

struct Stop {
    u32 stop_id;
    u32 station_id;
    f64 latitude;
    f64 longitude;

    Stop(u32 stop_id, u32 station_id, f64 latitude, f64 longitude)
        : stop_id(stop_id), station_id(station_id), latitude(latitude), longitude(longitude) {}
};

struct Conn {
    u32 trip_id;
    u32 from_stop_id;
    u32 to_stop_id;
    u32 departure_time;
    u32 arrival_time;

    Conn(u32 trip_id, u32 from_stop_id, u32 to_stop_id, u32 departure_time, u32 arrival_time)
    : trip_id(trip_id), from_stop_id(from_stop_id), to_stop_id(to_stop_id), departure_time(departure_time), arrival_time(arrival_time) {}
};

struct Path {
    u32 from_stop_id;
    u32 to_stop_id;
    u32 duration;

    Path(u32 from_stop_id, u32 to_stop_id, u32 duration)
        : from_stop_id(from_stop_id), to_stop_id(to_stop_id), duration(duration) {}
};

struct Network {
    vector<Stop> stops;
    vector<Conn> conns;
    vector<Path> paths;

    vector<vector<Stop*>> stations;
    vector<vector<Conn*>> trips;
};

#endif
