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
    u64 runtime_ns;
    vector<Journey> journeys;

    QueryResult(u64 runtime_ns)
        : runtime_ns(runtime_ns) {}
};

struct PreprocessingResult {
    u64 runtime_ns;

    PreprocessingResult(u64 runtime_ns)
        : runtime_ns(runtime_ns) {}
};

#endif
