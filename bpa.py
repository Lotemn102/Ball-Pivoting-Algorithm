from grid import Grid
from point import Point
from edge import Edge
import utils

import copy
import math


class BPA:
    def __init__(self, path, radius):
        # TODO: Do i really want this to be dynamic array?
        self.points = self.read_points(path) # "free points" will be on the beginning of the list, "used points" will
        # be on the end of the list.
        self.radius = radius
        self.grid = Grid(points=self.points, radius=radius)
        self.num_free_points = len(self.points)

    def read_points(self, path):
        points = []
        f = open(path, "r")
        lines = f.read().splitlines()

        for line in lines:
            coordinates = line.split()

            if len(coordinates) is 3:
                p = Point(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]))
                points.append(p)

            elif len(coordinates) is 6:
                p = Point(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]))
                normal = Point(float(coordinates[3]), float(coordinates[4]), float(coordinates[5]))
                p.normal = normal
                points.append(p)

            else:
                continue

        f.close()

        return points

    def find_seed_triangle(self) -> int:
        # Stop if there aren't any free points left.
        if self.num_free_points == 0 or self.num_free_points <= 2:
            return -1

        # TODO: Do i really want this to be done randomly?
        # Find a random free point.
        p1 = self.points[0]
        p1_neighbor_points = []

        # Find all points in 2r distance from that point.
        for cell in p1.neighbor_nodes:
            p1_neighbor_points.extend(self.grid.get_cell_points(cell))
            p2_neighbor_points = []

            # For each other point, find all points that are in 2r distance from that other point.
            for p2 in p1_neighbor_points:

                if p2.x == p1.x and p2.y == p1.y and p2.z == p1.z:
                    continue

                for sub_cell in p2.neighbor_nodes:
                    p2_neighbor_points.extend(self.grid.get_cell_points(sub_cell))

                    # For each three points we got, check if a sphere with a radius of r cant be fitted inside the
                    # triangle.
                    for p3 in p2_neighbor_points:

                        if (p3.x == p1.x and p3.y == p1.y and p3.z == p1.z) or (p2.x == p3.x and p2.y == p3.y and p2.z
                                                                                == p3.z):
                            continue

                        temp = utils.calc_incircle_radius(p1, p2, p3)

                        if self.radius <= utils.calc_incircle_radius(p1, p2, p3):
                            # Add the new edges.
                            self.grid.edges.append(Edge(p1, p2))
                            self.grid.edges.append(Edge(p1, p3))
                            self.grid.edges.append(Edge(p2, p3))

                            # Move the points to the end of the list.
                            self.points.remove(p1)
                            self.points.insert(len(self.points), p1)
                            self.num_free_points = self.num_free_points - 1

                            self.points.remove(p2)
                            self.points.insert(len(self.points), p2)
                            self.num_free_points = self.num_free_points - 1

                            self.points.remove(p3)
                            self.points.insert(len(self.points), p3)
                            self.num_free_points = self.num_free_points - 1
                            return 1

        # Else, find another free point and start over.
        self.points.remove(p1)
        self.points.insert(len(self.points), p1)
        self.num_free_points = self.num_free_points - 1
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
            t = utils.calc_incircle_radius(p1, p2, point)
            if self.radius <= utils.calc_incircle_radius(p1, p2, point):
                # Update that 'point' is not free anymore, so it won't be accidentally chosen in the seed search.
                self.points.remove(point)
                self.points.insert(len(self.points), point)
                self.num_free_points = self.num_free_points - 1

                self.grid.add_edge(Edge(p1, point))
                self.grid.add_edge(Edge(p2, point))
                break
        else: # Might not be trivial: Python has for/else structure...
            # If we can't keep going from this edge, remove it.
            if idx == len(possible_points)-1:
                self.grid.remove_edge(edge)
