#ifndef QUERIES_H
#define QUERIES_H

#include <vector>

#include "types.h"

using namespace std;

namespace JourneyBench {

    struct Query {
        u32 from_node_id;
        u32 to_node_id;
        u32 departure_time;
    };

    struct Queries {
        vector <Query> queries;
    };

}

#endif
