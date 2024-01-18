#include <cassert>

#include <algorithm>
#include <limits>

#include "algorithm.h"
#include "network.h"
#include "results.h"

#define INF numeric_limits<u32>::max()
#define EMPTY numeric_limits<u32>::max()

using namespace std;
namespace JB = JourneyBench;


namespace CSA {

    struct Conn {
        u32 dep_stop;
        u32 arr_stop;
        u32 dep_time;
        u32 arr_time;
        u32 trip;
        u32 index;  // Index in the original network data.
        Conn *prev;
    };

    struct Path {
        u32 dep_stop;
        u32 arr_stop;
        u32 dur;
        u32 index;  // Index in the original network data.
    };

    struct JourneyLeg {
        Conn *first_conn;
        Conn *last_conn;
        Path *path;
    };


    class CSAAlgorithm : public JB::AlgorithmBase {
        u32 conn_count = 0;
        u32 stop_count = 0;
        u32 trip_count = 0;
        u32 *path_count = nullptr;

        Conn *conns = nullptr;
        Path **paths = nullptr;

        /* Runtime data. */
        u32 *stops = nullptr;
        Conn **trips = nullptr;
        JourneyLeg *journeys = nullptr;

        bool initialized = false;


        int init(JB::Network *network) override {
            assert(!initialized);

            conn_count = network->conns.size();
            stop_count = network->nodes.size();
            trip_count = network->trips.size();
            path_count = new u32[stop_count]();
            fill_n(path_count, stop_count, 0);

            conns = new Conn[conn_count]();
            paths = new Path*[stop_count]();
            fill_n(paths, stop_count, nullptr);

            Conn *prev_conn[trip_count];
            fill_n(prev_conn, trip_count, nullptr);

            /* Load the connections. */
            for (u32 i = 0; i < conn_count; i++) {
                JB::Conn n_conn = network->conns[i];
                conns[i] = {
                        n_conn.from_node_id,
                        n_conn.to_node_id,
                        n_conn.departure_time,
                        n_conn.arrival_time,
                        n_conn.trip_id,
                        i,
                        prev_conn[n_conn.trip_id]
                };
                prev_conn[n_conn.trip_id] = &conns[i];
            }

            /* Load the paths. */
            for (u32 i = 0, count = 0, last_stop = INF; i < network->paths.size(); i++, count--) {
                JB::Path n_path = network->paths[i];

                if (n_path.node_a_id != last_stop) {
                    assert(count == 0);
                    for (u32 j = i; j < network->paths.size(); j++) {
                        if (network->paths[j].node_a_id != n_path.node_a_id) { break; }
                        count++;
                    }
                    path_count[n_path.node_a_id] = count;
                    paths[n_path.node_a_id] = new Path[count]();
                    last_stop = n_path.node_a_id;
                }

                paths[n_path.node_a_id][path_count[n_path.node_a_id] - count] = {
                        n_path.node_a_id,
                        n_path.node_b_id,
                        n_path.duration,
                        i
                };
            }

            stops = new u32[stop_count]();
            trips = new Conn*[trip_count]();
            journeys = new JourneyLeg[stop_count]();

            initialized = true;
            return 0;
        }

        JB::Journey *__query(u32 from_stop_id, u32 to_stop_id, u32 departure_time) {
            assert(initialized);
            assert(from_stop_id < stop_count && to_stop_id < stop_count);

            /* Clear the runtime datastructures. */
            fill_n(stops, stop_count, INF);
            fill_n(trips, trip_count, nullptr);
            fill_n(journeys, stop_count, (JourneyLeg) {nullptr, nullptr, nullptr});

            /* Set the initial state. */
            stops[from_stop_id] = departure_time;
            for (u32 i = 0; i < path_count[from_stop_id]; i++) {
                stops[paths[from_stop_id][i].arr_stop] = departure_time + paths[from_stop_id][i].dur;
                journeys[paths[from_stop_id][i].arr_stop].path = &paths[from_stop_id][i];
            }

            /* Run the search by walking through all connections. */
            for (u32 i = 0; i < conn_count; i++) {
                Conn conn = conns[i];

                /* Check if this connection is reachable. */
                if (trips[conn.trip] != nullptr || stops[conn.dep_stop] <= conn.dep_time) {
                    /* Save the first connection of the trip if needed. */
                    if (trips[conn.trip] == nullptr) {
                        trips[conn.trip] = &conns[i];
                    }

                    /* Check if the current connection improves the arrival time. */
                    if (conn.arr_time < stops[conn.arr_stop]) {
                        stops[conn.arr_stop] = conn.arr_time;
                        journeys[conn.arr_stop] = {
                                trips[conn.trip],
                                &conns[i],
                                nullptr
                        };

                        /* Check for improvements on each outgoing path. */
                        for (u32 j = 0; j < path_count[conn.arr_stop]; j++) {
                            Path path = paths[conn.arr_stop][j];
                            if (conn.arr_time + path.dur < stops[path.arr_stop]) {
                                stops[path.arr_stop] = conn.arr_time + path.dur;
                                journeys[path.arr_stop] = {
                                        trips[conn.trip],
                                        &conns[i],
                                        &paths[conn.arr_stop][j]
                                };
                            }
                        }
                    }
                }
            }

            /* Early return if no solution was found. */
            if (stops[to_stop_id] == INF) { return nullptr; }

            JB::Journey *journey = new JB::Journey();
            JourneyLeg *leg = &journeys[to_stop_id];
            while (to_stop_id != from_stop_id) {
                /* First: add the path if one is referenced, and update stop ID. */
                if (leg->path != nullptr) {
                    journey->add_prev_path(leg->path->index);
                    to_stop_id = leg->path->dep_stop;
                }

                /* Second: add the connections if they exist, and update stop ID. */
                if (leg->first_conn != nullptr) {
                    assert(leg->last_conn != nullptr);

                    /* Add each connection in the range from first to last. */
                    for (Conn *conn = leg->last_conn; conn != leg->first_conn->prev; conn = conn->prev) {
                        journey->add_prev_conn(conn->index);
                    }
                    to_stop_id = leg->first_conn->dep_stop;
                }

                assert(leg != &journeys[to_stop_id]);
                leg = &journeys[to_stop_id];
            }
            return journey;
        }

        vector <JB::Journey> *query(u32 from_stop_id, u32 to_stop_id, u32 departure_time) override {
            assert(initialized);

            vector <JB::Journey> *result = new vector<JB::Journey>;
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

}

using namespace CSA;

extern "C" CSAAlgorithm* createInstance() {
    return new CSAAlgorithm();
}
