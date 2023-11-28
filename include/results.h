#ifndef RESULTS_H
#define RESULTS_H

#include <vector>

#include "types.h"

using namespace std;

namespace JourneyBench {

    enum JourneyPartType {
        CONN, PATH
    };

    struct JourneyPart {
        JourneyPartType type;
        u32 id;

        JourneyPart(JourneyPartType type, u32 id)
                : type(type), id(id) {}
    };

    struct Journey {
        vector <JourneyPart> parts;

        inline void add_next_conn(u32 conn_id) {
            parts.push_back(JourneyPart(JourneyPartType::CONN, conn_id));
        }
        inline void add_prev_conn(u32 conn_id) {
            parts.insert(parts.begin(), JourneyPart(JourneyPartType::CONN, conn_id));
        }

        inline void add_next_path(u32 path_id) {
            parts.push_back(JourneyPart(JourneyPartType::PATH, path_id));
        }
        inline void add_prev_path(u32 path_id) {
            parts.insert(parts.begin(), JourneyPart(JourneyPartType::PATH, path_id));
        }
    };

    struct QueryResult {
        u64 runtime_ns;
        vector <Journey> journeys;

        QueryResult(u64 runtime_ns)
                : runtime_ns(runtime_ns) {}
        QueryResult(u64 runtime_ns, vector <Journey> journeys)
                : runtime_ns(runtime_ns), journeys(journeys) {}
    };

    struct PreprocessingResult {
        u64 runtime_ns;

        PreprocessingResult(u64 runtime_ns)
                : runtime_ns(runtime_ns) {}
    };

}

#endif
