from datetime import datetime, timedelta

from benchmark import Network, Queries


def td(delta: int) -> timedelta:
    return timedelta(seconds=delta)

# Example network topology:
#       2 * - - - * 3   (from 2 to 3 is footpath)
#        /         \
#     1 *           * 4
#      /             \
#   0 * ------------> * 5


S = datetime(2023, 1, 1, 9, 0, 0)  # 2023-01-01 09:00:00
E = S + timedelta(minutes=30)

network = Network(S, E)
network.add_stop(0, 0, 0)
network.add_stop(1, 1, 1)
network.add_stop(2, 2, 2)
network.add_stop(3, 2, 3)
network.add_stop(4, 1, 4)
network.add_stop(5, 0, 5)
network.add_conn(0, 0, 1, S, S + td(150))
network.add_conn(0, 1, 2, S + td(150), S + td(300))
network.add_conn(1, 3, 4, S + td(600), S + td(750))
network.add_conn(1, 4, 5, S + td(750), S + td(900))
network.add_conn(2, 0, 5, S + td(600), S + td(1200))
network.add_path(2, 3, td(150))
network.write('data/Example/Example.network')

queries = Queries()
queries.add_query(0, 5, 0)
queries.write('data/Example/Example.queries')
