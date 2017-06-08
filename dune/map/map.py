from dune.map.graph import Graph
from dune.state.spaces import SPACES, EDGES


class MapGraph:
    def __init__(self):
        self.g = Graph()

        # Add sector 0's
        for name, type, _, _, sectors in SPACES:
            for s in sectors:
                self.g.add_node((name, s))
            for s1 in sectors:
                for s2 in sectors:
                    if abs(s1-s2) == 1:
                        self.g.add_edge((name, s1), (name, s2), 0)

        # Add edges
        for (a, b) in EDGES:
            self.g.add_edge(a, b, 1)
            self.g.add_edge(b, a, 1)

    def remove_sector(self, sector):
        for n in set(self.g.nodes):
            if n[1] == sector:
                self.g.remove_node(n)

    def remove_space(self, space):
        for n in set(self.g.nodes):
            if n[0] == space:
                self.g.remove_node(n)

    def deadend_sector(self, sector):
        for n in set(self.g.nodes):
            if n[1] == sector:
                for e in set(self.g.edges[n]):
                    self.g.remove_edge(n, e)

    def valid_destinations(self, space, sector, distance):
        nodes = self.g.get_distances((space, sector))
        valid_destinations = []
        for n in nodes:
            if nodes[n] <= distance:
                valid_destinations.append(n)
        return valid_destinations

    def distance(self, space_a, sector_a, space_b, sector_b):
        return self.g.distance((space_a, sector_a), (space_b, sector_b))
