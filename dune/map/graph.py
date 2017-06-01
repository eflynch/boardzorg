import numpy as np


class Node:
    def __init__(self):
        self.name


class Graph:
    def __init__(self, nodes):
        self.nodes = nodes

        self.matrix = np.zeros((len(nodes), len(nodes)), dtype=bool)

    def add_edge(self, a, b):
        i = self.nodes.index(a)
        j = self.nodes.index(b)
        self.matrix[i, j] = True
        self.matrix[j, i] = True

    def remove_edge(self, a, b):
        i = self.nodes.index(a)
        j = self.nodes.index(b)
        self.matrix[i, j] = False
        self.matrix[j, i] = False

    def check_edge(self, a, b):
        i = self.nodes.index(a)
        j = self.nodes.index(b)
        return self.matrix[i, j]

    def list_adjacencies(self, a):
        i = self.nodes.index(a)
        adjacencies = []
        for j in range(len(self.nodes)):
            if self.matrix[i, j]:
                adjacencies.append(self.nodes[j])

        return adjacencies
