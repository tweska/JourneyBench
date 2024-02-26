import sys
from typing import List, Union, Tuple

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


def check_journey(reconstructed_journey, from_node_id, to_node_id, departure_time) -> Tuple[bool, bool, int]:
    logic = True
    visited_nodes = [from_node_id]
    current_node = from_node_id
    current_time = departure_time
    for part in reconstructed_journey:
        if type(part) is Conn:
            prev_node = part.from_node_id
            next_node = part.to_node_id
            if part.departure_time < current_time:
                print("Departure time is before current time!", file=sys.stderr)
                return False, False, -1
            current_time = part.arrival_time
        else:
            assert type(part) is Path
            if current_node == part.node_a_id:
                prev_node = part.node_a_id
                next_node = part.node_b_id
            else:
                prev_node = part.node_b_id
                next_node = part.node_a_id
            current_time += part.duration

        if prev_node != current_node:
            print("Journey contains teleportation!", file=sys.stderr)
            return False, False, -1
        if next_node in visited_nodes:
            print("Journey contains loop!", file=sys.stderr)
            logic = False
        current_node = next_node

    if current_node != to_node_id:
        print("Journey does not reach destination!", file=sys.stderr)
        return False, False, -1
    return True, logic, current_time


def print_reconstructed(reconstructed_journey):
    parts = []
    for part in reconstructed_journey:
        if type(part) is Conn:
            parts.append(f"Conn(trip={part.trip_id}, dep_node={part.from_node_id}, arr_node={part.to_node_id}, dep_time={part.departure_time}, arr_time={part.arrival_time})")
        else:
            assert type(part) is Path
            parts.append(f"Path(dep_node={part.node_a_id}, arr_node={part.node_b_id}, duration={part.duration})")
    print(" -> ".join(parts))
