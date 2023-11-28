#ifndef CSA_DATA_H
#define CSA_DATA_H

#include <cstddef>
#include <cstdint>

#include "network.h"

namespace CSA {

    struct Conn {
        uint32_t dep_stop;
        uint32_t arr_stop;
        uint32_t dep_time;
        uint32_t arr_time;
        uint32_t trip;
    };

    struct Path {
        uint32_t dep_stop;
        uint32_t arr_stop;
        uint32_t dur;
    };

    struct Stop {
        size_t path_count;
        Path *paths;
    };

    struct Data {
        size_t conn_count;
        size_t path_count;
        size_t stop_count;
        size_t trip_count;

        Conn *conns;
        Path *paths;
        Stop *stops;
    };

    Data *read_data(JourneyBench::Network *network);

}

#endif
