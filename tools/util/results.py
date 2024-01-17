
from typing import List, Union

from benchmark import Network, Journey, Conn, Path, JourneyPartType


def reconstruct_journey(network: Network, journey: Journey) -> List[Union[Conn, Path]]:
    result = []
    for part in journey.parts:
        if part.type == JourneyPartType.CONN:
            result.append(network.conns[part.id])
        else:
            assert part.type == JourneyPartType.PATH
            result.append(network.paths[part.id])
    return result


def is_legal_journey(reconstructed_journey, from_node_id, to_node_id, departure_time) -> bool:
    visited_nodes = [from_node_id]
    current_node = from_node_id
    current_time = departure_time
    for part in reconstructed_journey:
        if type(part) is Conn:
            prev_node = part.from_node_id
            next_node = part.to_node_id
            if part.departure_time < current_time:
                return False
            current_time = part.arrival_time
        else:
            assert type(part) is Path
            prev_node = part.node_a_id
            next_node = part.node_b_id
            current_time += part.duration

        if prev_node != current_node:
            return False
        if next_node in visited_nodes:
            return False
        current_node = next_node

    return current_node == to_node_id
