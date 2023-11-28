#ifndef ALGOBASE_H
#define ALGOBASE_H

#include <cstdint>

#include "network.h"
#include "results.h"
#include "types.h"

namespace JourneyBench {

    class AlgorithmBase {
    public:
        virtual int init(Network *network) = 0;

        virtual vector <Journey> *query(u32 from_node_id, u32 to_node_id, u32 departure_time) = 0;
    };

}

#endif
