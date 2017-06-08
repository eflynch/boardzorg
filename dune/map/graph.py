from collections import defaultdict


class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def remove_node(self, value):
        self.nodes.remove(value)
        for e in self.edges:
            if value in self.edges[e]:
                self.edges[e].remove(value)
            if (e, value) in self.distances:
                del self.distances[(e, value)]
            if (value, e) in self.distances:
                del self.distances[(value, e)]

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.distances[(from_node, to_node)] = distance

    def remove_edge(self, from_node, to_node):
        if to_node in self.edges[from_node]:
            self.edges[from_node].remove(to_node)
        if (from_node, to_node) in self.distances:
            del self.distances[(from_node, to_node)]

    def get_distances(self, from_node):
        return dijsktra(self, from_node)[0]

    def distance(self, from_node, to_node):
        distances, path = dijsktra(self, from_node)
        if to_node in distances:
            return distances[to_node]
        return float("inf")


def dijsktra(graph, initial):
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            weight = current_weight + graph.distances[(min_node, edge)]
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path


if __name__ == "__main__":
    g = Graph()
    for a in "ABCDEFGH":
        g.add_node(a)


    g.add_edge("A", "B", 0)
    g.add_edge("B", "C", 1)
    g.add_edge("C", "D", 0)
    g.add_edge("D", "C", 0)
    g.remove_node("B")

    print(g.distance("A", "D"))
