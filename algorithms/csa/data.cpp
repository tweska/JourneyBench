#include <cstddef>
#include <cstdint>

#include "network.h"
#include "data.h"

using namespace CSA;

namespace CSA {
    Data *read_data(Network *network) {
        Data *data = new Data{};

        /* Initialize the counters. */
        data->conn_count = network->conn_count;
        data->path_count = network->path_count;
        data->stop_count = network->stop_count;
        data->trip_count = network->trip_count;

        /* Initialize the arrays. */
        data->conns = new Conn[data->conn_count]{};
        data->paths = new Path[data->path_count]{};
        data->stops = new Stop[data->stop_count]{};

        /* Load the connections. */
        for (size_t i = 0; i < data->conn_count; i++) {
            NetworkConn n_conn = network->conns[i];
            Conn *conn = &data->conns[i];
            conn->dep_stop = n_conn.from_stop_id;
            conn->arr_stop = n_conn.to_stop_id;
            conn->dep_time = n_conn.departure_time;
            conn->arr_time = n_conn.arrival_time;
            conn->trip = n_conn.trip_id;
        }

        /* Load the paths. */
        for (size_t i = 0; i < data->path_count; i++) {
            NetworkPath n_path = network->paths[i];
            Path *path = &data->paths[i];
            path->arr_stop = n_path.to_stop_id;
            path->dur = n_path.duration;

            Stop *dep_stop = &data->stops[n_path.from_stop_id];
            if (dep_stop->path_count == 0) {
                dep_stop->paths = path;
            }
            dep_stop->path_count++;
        }

        return data;
    }
}
