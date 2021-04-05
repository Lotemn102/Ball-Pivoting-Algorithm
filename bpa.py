from grid import Grid
from point import Point
from edge import Edge
import utils

import copy
import math


class BPA:
    def __init__(self, path, radius):
        points = self.read_points(path)
        # TODO: Do i really want this to be dynamic array?
        self.free_points = copy.deepcopy(points)
        self.radius = radius
        self.grid = Grid(points=points, radius=radius)

    def read_points(self, path):
        points = []
        f = open(path, "r")
        lines = f.read().splitlines()

        for line in lines:
            coordinates = line.split()

            if len(coordinates) is not 3:
                continue

            p = Point(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]))
            points.append(p)

        f.close()

        return points

    def find_seed_triangle(self) -> int:
        # Stop if there aren't any free points left.
        if len(self.free_points) == 0 or len(self.free_points) <= 2:
            return -1

        # TODO: Do i really want this to be done randomly?
        # Find a random free point.
        p1 = self.free_points[0]
        p1_neighbor_points = []

        # Find all points in 2r distance from that point.
        for cell in p1.neighbor_nodes:
            p1_neighbor_points.extend(self.grid.get_cell_points(cell))
            p2_neighbor_points = []

            # For each other point, find all points that are in 2r distance from that other point.
            for p2 in p1_neighbor_points:
                for sub_cell in p2.neighbor_nodes:
                    p2_neighbor_points.extend(self.grid.get_cell_points(sub_cell))

                    # For each three points we got, check if a sphere with a radius of r cant be fitted inside the
                    # triangle.
                    for p3 in p2_neighbor_points:
                        if self.radius <= utils.calc_incircle_radius(p1, p2, p3):
                            # Add the new edges.
                            self.grid.edges.append(Edge(p1, p2))
                            self.grid.edges.append(Edge(p1, p3))
                            self.grid.edges.append(Edge(p2, p3))

                            # Remove points from free points list.
                            self.free_points.remove(p1)
                            self.free_points.remove(p2)
                            self.free_points.remove(p3)
                            return 1

        # Else, find another free point and start over.
        self.free_points.remove(p1)
        return self.find_seed_triangle()

    def create_mesh(self):
        pass

    def expand_triangle(self, edge: Edge):
        # Avoid duplications.
        intersect_cells = list(set(edge.p1.neighbor_nodes) & set(edge.p2.neighbor_nodes))
        possible_points = []
        idx = 0

        p1, p2 = edge.p1, edge.p2

        for cell in intersect_cells:
            possible_points.extend(self.grid.get_cell_points(cell))

        for idx, point in enumerate(possible_points):
            # If a sphere's radius is smaller than the radius of the incircle of a triangle, the sphere can fit into the
            # triangle.
            if self.radius <= utils.calc_incircle_radius(p1, p2, point):
                # Update that 'point' is not free anymore, so it won't be accidentally chosen in the seed search.
                self.free_points.remove(point)

                self.grid.add_edge(Edge(p1, point))
                self.grid.add_edge(Edge(p2, point))
                break
        else: # Might not be trivial: Python has for/else structure...
            # If we can't keep going from this edge, remove it.
            if idx == len(possible_points):
                self.grid.remove_edge(edge)
