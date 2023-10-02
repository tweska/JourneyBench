#include <google/protobuf/message.h>

#include <fstream>

#include "network.h"
#include "network.pb.h"
#include "networkreader.h"

using namespace network;
using namespace std;

Network *read_network(char *filepath) {
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    PBNetwork pbNetwork;
    {
        fstream input(filepath, ios::in | ios::binary);
        if (!pbNetwork.ParseFromIstream(&input)) { return NULL; }
    }

    Network *network = new Network{};

    /* Get array lengths. */
    network->stop_count = pbNetwork.stops_size();
    network->conn_count = pbNetwork.conns_size();
    network->path_count = pbNetwork.paths_size();
    network->station_count = pbNetwork.station_count();
    network->trip_count = pbNetwork.trip_count();

    /* Reserve memory for the arrays. */
    network->stops = new NetworkStop[network->stop_count]{};
    network->conns = new NetworkConn[network->conn_count]{};
    network->paths = new NetworkPath[network->path_count]{};
    network->stations = new NetworkStop*[network->station_count]{};
    network->trips = new NetworkConn*[network->trip_count]{};

    /* Copy the stops. */
    for (uint32_t i = 0; i < network->stop_count; i++) {
        PBNetworkStop pbStop = pbNetwork.stops(i);
        NetworkStop *stop = &network->stops[i];

        stop->stop_id = i;
        stop->station_id = pbStop.station_id();
        stop->latitude = pbStop.latitude();
        stop->longitude = pbStop.longitude();

        NetworkStop **next_ptr_loc = &network->stations[stop->station_id];
        while (*next_ptr_loc != NULL) {
            next_ptr_loc = &(*next_ptr_loc)->next_in_station;
        }
        (*next_ptr_loc) = stop;
    }

    /* Copy the connections. */
    for (uint32_t i = 0; i < network->conn_count; i++) {
        PBNetworkConn pbConn = pbNetwork.conns(i);
        NetworkConn *conn = &network->conns[i];

        conn->trip_id = pbConn.trip_id();
        conn->from_stop_id = pbConn.from_stop_id();
        conn->to_stop_id = pbConn.to_stop_id();
        conn->departure_time = pbConn.departure_time();
        conn->arrival_time = pbConn.arrival_time();

        NetworkConn **next_ptr_loc = &network->trips[conn->trip_id];
        while (*next_ptr_loc != NULL) {
            next_ptr_loc = &(*next_ptr_loc)->next_in_trip;
        }
        (*next_ptr_loc) = conn;
    }

    /* Copy the paths. */
    for (uint32_t i = 0; i < network->path_count; i++) {
        PBNetworkPath pbPath = pbNetwork.paths(i);
        NetworkPath *path = &network->paths[i];

        path->from_stop_id = pbPath.from_stop_id();
        path->to_stop_id = pbPath.to_stop_id();
        path->duration = pbPath.duration();
    }

    google::protobuf::ShutdownProtobufLibrary();
    return network;
}
