#include <algorithm>
#include <limits>

#include <iostream>

#include "algorithm.h"
#include "network.h"
#include "results.h"
#include "data.h"

using namespace std;
using namespace CSA;
namespace JB = JourneyBench;

struct crumb {
    bool is_conn;
    u32 id;
};

class CSAAlgorithm : public JB::AlgorithmBase {
    Data *data = NULL;

    int init(JB::Network *network) override {
        data = read_data(network);
        return data == NULL;
    }

    JB::Journey *__query(u32 from_stop_id, u32 to_stop_id, u32 departure_time) {
        static Stop dep_stop = data->stops[from_stop_id];

        /* Initialize the stop times. */
        u32 stops[data->stop_count];
        crumb trail[data->stop_count];
        for (u32 i = 0; i < data->stop_count; i++) {
            stops[i] = numeric_limits<u32>::max();
        }
        for (u32 i = 0; i < dep_stop.path_count; i++) {
            stops[dep_stop.paths[i].arr_stop] = departure_time + dep_stop.paths[i].dur;
            trail[dep_stop.paths[i].arr_stop] = { false, i };
        }
        stops[from_stop_id] = departure_time;

        /* Initialize the trips. */
        bool trips[data->trip_count]{};

        /* Do the search. */
        for (u32 i = 0; i < data->conn_count; i++) {
            Conn conn = data->conns[i];
            if (trips[conn.trip] || stops[conn.dep_stop] <= conn.dep_time) {
                trips[conn.trip] = true;
                if (stops[conn.arr_stop] > conn.arr_time) {
                    stops[conn.arr_stop] = conn.arr_time;
                    trail[conn.arr_stop] = { true, i };
                }

                Stop arr_stop = data->stops[conn.arr_stop];
                for (u32 j = 0; j < arr_stop.path_count; j++) {
                    Path path = arr_stop.paths[j];
                    stops[path.arr_stop] = min(stops[path.arr_stop], conn.arr_time + path.dur);
                    trail[path.arr_stop] = { false, j };
                }
            }
        }

        if (stops[to_stop_id] == numeric_limits<u32>::max()) {
            return nullptr;
        }

        JB::Journey *journey = new JB::Journey();
        u32 stop_id = to_stop_id;
        while (stop_id != from_stop_id) {

            if (trail[stop_id].is_conn) {
                journey->add_prev_conn(trail[stop_id].id);
                stop_id = data->conns[trail[stop_id].id].dep_stop;
            } else {
                journey->add_prev_path(trail[stop_id].id);
                stop_id = data->paths[trail[stop_id].id].dep_stop;
            }
        }
        return journey;
    }

    vector<JB::Journey> *query(u32 from_stop_id, u32 to_stop_id, u32 departure_time) {
        if (data == NULL) { return nullptr; }

        vector<JB::Journey> *result = new vector<JB::Journey>;
        if (from_stop_id == to_stop_id) {
            result->push_back(JB::Journey());
            return result;
        }
        JB::Journey *journey = __query(from_stop_id, to_stop_id, departure_time);
        if (journey == nullptr) {
            return result;
        }
        result->push_back(*journey);
        delete journey;
        return result;
    }
};

extern "C" CSAAlgorithm* createInstance() {
    return new CSAAlgorithm();
}
