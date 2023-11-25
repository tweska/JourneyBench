#include <iostream>

#include "algorithm.h"
#include "network.h"
#include "results.h"
#include "types.h"

using namespace std;

// TODO: Choose base class(es) based on algorithm capabilities.
class ExampleAlgorithm : public AlgorithmBase {
    int init(Network *network) override {
        (void) network;
        cerr << "Initializing ExampleAlgorithm!" << endl;
        // TODO: Implement reading input (and preprocessing) here!
        return 0;
    }

    vector<Journey> *query(u32 from_node_id, u32 to_node_id, u32 departure_time) {
        cerr << "Running query from " << from_node_id << " to " << to_node_id << " at time " << departure_time << endl;
        // TODO: Implement query here!

        Journey journey = Journey();

        JourneyLeg leg1 = JourneyLeg(LegType::CONN);
        JourneyLeg leg2 = JourneyLeg(LegType::PATH);
        JourneyLeg leg3 = JourneyLeg(LegType::CONN);

        leg1.parts.push_back(0);
        leg1.parts.push_back(1);
        leg2.parts.push_back(0);
        leg3.parts.push_back(2);
        leg3.parts.push_back(3);

        journey.legs.push_back(leg1);
        journey.legs.push_back(leg2);
        journey.legs.push_back(leg3);

        vector<Journey> *result = new vector<Journey>();
        result->push_back(journey);
        return result;
    }
};

extern "C" ExampleAlgorithm* createInstance() {
    return new ExampleAlgorithm();
}
