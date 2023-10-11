#ifndef ALGOBASE_H
#define ALGOBASE_H

#include <cstdint>

#include "network.h"
#include "types.h"

class AlgorithmBase {
public:
    virtual int init(Network *network) = 0;
};

class AlgorithmEAT : public AlgorithmBase {
public:
    virtual int query_eat(u32 from_stop_id, u32 to_stop_id, u32 departure_time) = 0;
};

class AlgorithmBiC : public AlgorithmBase {
public:
    virtual int query_bic(u32 from_stop_id, u32 to_stop_id, u32 departure_time) = 0;
};

#endif
