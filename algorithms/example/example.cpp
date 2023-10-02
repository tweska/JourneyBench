#include <iostream>

#include "algobase.h"

using namespace std;

// TODO: Choose base class(es) based on algorithm capabilities.
class ExampleAlgorithm : public AlgorithmEAT, public AlgorithmBiC {
    int init(Network *network) override {
        (void) network;
        cerr << "Initializing ExampleAlgorithm!" << endl;
        // TODO: Implement reading input (and preprocessing) here!
        return -1;
    }

    int query_eat(uint32_t from_stop_id, uint32_t to_stop_id, uint32_t departure_time) {
        cerr << "Running EAT query from " << from_stop_id << " to " << to_stop_id << " at time " << departure_time << endl;
        // TODO: Implement EAT query here!
        return -1;
    }

    int query_bic(uint32_t from_stop_id, uint32_t to_stop_id, uint32_t departure_time) {
        cerr << "Running BiC query from " << from_stop_id << " to " << to_stop_id << " at time " << departure_time << endl;
        // TODO: Implement BiC query here!
        return -1;
    }
};

extern "C" ExampleAlgorithm* createInstance() {
    return new ExampleAlgorithm();
}
