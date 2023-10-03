#include <algorithm>
#include <limits>

#include "algobase.h"
#include "network.h"
#include "data.h"

using namespace std;
using namespace CSA;

class CSAAlgorithm : public AlgorithmEAT {
    Data *data = NULL;

    int init(Network *network) override {
        data = read_data(network);
        return data == NULL;
    }

    int query_eat(uint32_t from_stop_id, uint32_t to_stop_id, uint32_t departure_time) {
        if (data == NULL) { return -1; }

        static Stop dep_stop = data->stops[from_stop_id];

        /* Initialize the stop times. */
        uint32_t stops[data->stop_count];
        for (size_t i = 0; i < data->stop_count; i++) {
            stops[i] = numeric_limits<uint32_t>::max();
        }
        for (size_t i = 0; i < dep_stop.path_count; i++) {
            stops[dep_stop.paths[i].arr_stop] = departure_time + dep_stop.paths[i].dur;
        }
        stops[from_stop_id] = departure_time;

        /* Initialize the trips. */
        bool trips[data->trip_count]{};

        /* Do the search. */
        for (size_t i = 0; i < data->conn_count; i++) {
            Conn conn = data->conns[i];
            if (trips[conn.trip] || stops[conn.dep_stop] <= departure_time) {
                trips[conn.trip] = true;
                stops[conn.arr_stop] = min(stops[conn.arr_stop], conn.arr_time);
                Stop arr_stop = data->stops[conn.arr_stop];
                for (size_t j = 0; j < arr_stop.path_count; j++) {
                    Path path = arr_stop.paths[j];
                    stops[path.arr_stop] = min(stops[path.arr_stop], conn.arr_time + path.dur);
                }
            }
        }

        return 0;
    }
};

extern "C" CSAAlgorithm* createInstance() {
    return new CSAAlgorithm();
}
