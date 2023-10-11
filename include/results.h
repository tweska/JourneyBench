#ifndef RESULTS_H
#define RESULTS_H

#include <vector>

#include "types.h"

using namespace std;

enum LegType { CONN, PATH };

struct JourneyLeg {
    LegType type;
    vector<u32> parts;

    JourneyLeg(LegType type) : type(type) {}
    JourneyLeg(LegType type, vector<u32> parts) : type(type), parts(parts) {}
};

struct Journey {
    vector<JourneyLeg> legs;
};

struct QueryResult {
    f64 execution_time_ms;
    vector<Journey> journeys;

    QueryResult(f64 execution_time_ms)
        : execution_time_ms(execution_time_ms) {}
};

#endif
