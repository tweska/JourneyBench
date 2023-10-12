#include <iostream>

#include "algobase.h"
#include "network.h"
#include "results.h"
#include "types.h"

using namespace std;

// TODO: Choose base class(es) based on algorithm capabilities.
class ExampleAlgorithm : public AlgorithmEAT, public AlgorithmBiC {
    int init(Network *network) override {
        (void) network;
        cerr << "Initializing ExampleAlgorithm!" << endl;
        // TODO: Implement reading input (and preprocessing) here!
        return 0;
    }

    Journey *query_eat(u32 from_stop_id, u32 to_stop_id, u32 departure_time) {
        cerr << "Running EAT query from " << from_stop_id << " to " << to_stop_id << " at time " << departure_time << endl;
        // TODO: Implement EAT query here!

        Journey *result = new Journey();

        JourneyLeg leg1 = JourneyLeg(LegType::CONN);
        JourneyLeg leg2 = JourneyLeg(LegType::PATH);
        JourneyLeg leg3 = JourneyLeg(LegType::CONN);

        leg1.parts.push_back(0);
        leg1.parts.push_back(1);
        leg2.parts.push_back(0);
        leg3.parts.push_back(2);
        leg3.parts.push_back(3);

        result->legs.push_back(leg1);
        result->legs.push_back(leg2);
        result->legs.push_back(leg3);

        return result;
    }

    vector<Journey> *query_bic(u32 from_stop_id, u32 to_stop_id, u32 departure_time) {
        cerr << "Running BiC query from " << from_stop_id << " to " << to_stop_id << " at time " << departure_time << endl;
        // TODO: Implement BiC query here!

        vector<Journey> *result = new vector<Journey>();

        Journey journey1 = Journey();
        JourneyLeg leg1 = JourneyLeg(LegType::CONN);
        leg1.parts.push_back(4);
        journey1.legs.push_back(leg1);
        result->push_back(journey1);
        result->push_back(*query_eat(from_stop_id, to_stop_id, departure_time));

        return result;
    }
};

extern "C" ExampleAlgorithm* createInstance() {
    return new ExampleAlgorithm();
}
