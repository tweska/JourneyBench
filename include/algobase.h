#ifndef ALGOBASE_H
#define ALGOBASE_H

#include <cstdint>

#include "network.h"

class AlgorithmBase {
public:
    virtual int init(Network *network) = 0;
};

class AlgorithmEAT : public AlgorithmBase {
public:
    virtual int query_eat(uint32_t from_stop_id, uint32_t to_stop_id, uint32_t departure_time) = 0;
};

class AlgorithmBiC : public AlgorithmBase {
public:
    virtual int query_bic(uint32_t from_stop_id, uint32_t to_stop_id, uint32_t departure_time) = 0;
};

#endif
