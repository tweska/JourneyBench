#include "queries.h"
#include "types.h"

#include "query_functions.h"

u32 add_query(Queries &queries,
              u32 from_node_id, u32 to_node_id,
              u32 departure_time) {
    queries.queries.push_back({
        from_node_id, to_node_id,
        departure_time
    });
    return queries.queries.size() - 1;
}
