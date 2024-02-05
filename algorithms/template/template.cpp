#include "algorithm.h"
#include "network.h"
#include "results.h"
#include "types.h"

namespace JB = JourneyBench;


class Algorithm : public JB::AlgorithmBase {

    int init(JB::Network *network) override {

        /* Prepare the algorithm specific datastructure.
         * If needed, you should also do the preprocessing here. */

        return 0;
    }

    vector <JB::Journey> *query(u32 from_stop_id, u32 to_stop_id, u32 departure_time) override {

        /* Answer the actual query here.
         * You may assume that the `init` function is already called at this point. */

        return nullptr;
    }

};


extern "C" Algorithm* createInstance() {
    return new Algorithm();
}
