#ifndef QUERIES_H
#define QUERIES_H

#include <vector>

#include "types.h"

using namespace std;

struct Query {
    u32 from_stop_id;
    u32 to_stop_id;
    u32 departure_time;

    Query(u32 from_stop_id, u32 to_stop_id, u32 departure_time)
        : from_stop_id(from_stop_id), to_stop_id(to_stop_id), departure_time(departure_time) {}
};

struct Queries {
    vector<Query> queries;
};

#endif
