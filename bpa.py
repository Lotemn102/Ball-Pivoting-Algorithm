from grid import Grid
from point import Point
from edge import Edge
import utils
import open3d as o3d
import numpy as np
import copy
from typing import Tuple


class BPA:
    def __init__(self, path, radius, visualizer=False):
        # TODO: Do i really want this to be dynamic array?
        self.points = self.read_points(path) # "free points" will be on the beginning of the list, "used points" will
        # be on the end of the list.
        self.const_points = copy.deepcopy(self.points) # For visualizing
        self.radius = radius
        self.grid = Grid(points=self.points, radius=radius)
        self.num_free_points = len(self.points)
        self.vis = None

        if visualizer is True:
            self.vis = self.init_visualizer()

    def init_visualizer(self):
        pcd = o3d.geometry.PointCloud()
        points = np.array([(point.x, point.y, point.z) for point in self.const_points])
        pcd.points = o3d.utility.Vector3dVector(points)

        # Color the point in black.
        points_mask = np.zeros(shape=(len(self.const_points), 3))
        black_colors = np.zeros_like(points_mask)
        pcd.colors = o3d.Vector3dVector(black_colors)

        # Set up visualizer.
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(pcd)
        return vis

    def update_visualizer(self, color='red'):
        """
        Updating only the edges (assuming points don't change).

        :return: None
        """
        if color == 'red':
            c = [1, 0, 0]
        elif color == 'green':
            c = [0, 1, 0]
        else:
            c = [0, 0, 1]

        lines = [[edge.p1.id, edge.p2.id] for edge in self.grid.edges]
        colors = [c for _ in range(len(lines))]
        line_set = o3d.geometry.LineSet()
        points = np.array([(point.x, point.y, point.z) for point in self.const_points])
        line_set.points = o3d.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)

        self.vis.add_geometry(line_set)
        self.vis.update_geometry()
        self.vis.poll_events()
        self.vis.update_renderer()

    def read_points(self, path):
        points = []
        f = open(path, "r")
        lines = f.read().splitlines()

        for i, line in enumerate(lines):
            coordinates = line.split()

            if len(coordinates) is 3:
                p = Point(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]), id=i)
                points.append(p)

            elif len(coordinates) is 6:
                p = Point(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]), id=i)
                normal = Point(float(coordinates[3]), float(coordinates[4]), float(coordinates[5]), id=i)
                p.normal = normal
                points.append(p)

            else:
                continue

        f.close()

        # Sorting the points can lead to better seed triangle picking
        sorted_points = sorted(points, key=lambda p: (p.x, p.y, p.z))

        for i, p in enumerate(sorted_points):
            p.id = i

        return sorted_points

    def find_seed_triangle(self) -> (int, Tuple):
        # Stop if there aren't any free points left.
        if self.num_free_points == 0 or self.num_free_points <= 2:
            return -1, None

        # TODO: Do i really want this to be done randomly?
        # Find a random free point.
        p1 = self.points[0]
        p1_neighbor_points = []

        # Find all points in 2r distance from that point.
        for cell in p1.neighbor_nodes:
            p1_neighbor_points.extend(self.grid.get_cell_points(cell))

            # For each other point, find all points that are in 2r distance from that other point.
            for p2 in p1_neighbor_points:

                if p2.x == p1.x and p2.y == p1.y and p2.z == p1.z:
                    continue

                # Find all points that are on 2r distance from p1 and p2
                intersect_cells = list(set(p1.neighbor_nodes) & set(p2.neighbor_nodes))
                possible_points = []

                for cell in intersect_cells:
                    possible_points.extend(self.grid.get_cell_points(cell))

                for p3 in possible_points:
                    if (p3.x == p1.x and p3.y == p1.y and p3.z == p1.z) or (p2.x == p3.x and p2.y == p3.y and p2.z
                                                                            == p3.z):
                        continue

                    temp = utils.calc_incircle_radius(p1, p2, p3)

                    # For each three points we got, check if a sphere with a radius of r cant be fitted inside the
                    # triangle.
                    if self.radius <= utils.calc_incircle_radius(p1, p2, p3):
                        # Add the new edges.
                        e1 = Edge(p1, p2)
                        e2 = Edge(p1, p3)
                        e3 = Edge(p2, p3)
                        self.grid.edges.append(e1)
                        self.grid.edges.append(e2)
                        self.grid.edges.append(e3)

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
                        return 1, (e1, e2, e3)

        # Else, find another free point and start over.
        self.points.remove(p1)
        self.points.insert(len(self.points), p1)
        self.num_free_points = self.num_free_points - 1
        return self.find_seed_triangle(), None

    def create_mesh(self):
        while 1:
            # Find a seed triangle.
            _, edges = self.find_seed_triangle()
            self.update_visualizer(color='red')

            # Try to expand from each
            for edge in edges:
                if self.expand_triangle(edge):
                    self.update_visualizer(color='green')
                    break

    def expand_triangle(self, edge: Edge) -> bool:
        # Avoid duplications.
        intersect_cells = list(set(edge.p1.neighbor_nodes) & set(edge.p2.neighbor_nodes))
        possible_points = []
        idx = 0

        p1, p2 = edge.p1, edge.p2

        for cell in intersect_cells:
            possible_points.extend(self.grid.get_cell_points(cell))

        for idx, point in enumerate(possible_points):

            if point.id == p1.id or point.id == p2.id:
                continue

            p1_and_point_already_connected = len([e for e in self.grid.edges if (e.p1.id == p1.id)
                                                  and (e.p2.id == point.id)]) > 0
            p2_and_point_already_connected = len([e for e in self.grid.edges if (e.p1.id == p2.id)
                                                  and (e.p2.id == point.id)]) > 0

            if p1_and_point_already_connected or p2_and_point_already_connected:
                continue

            # If a sphere's radius is smaller than the radius of the incircle of a triangle, the sphere can fit into the
            # triangle.
            if self.radius <= utils.calc_incircle_radius(p1, p2, point):
                # Update that 'point' is not free anymore, so it won't be accidentally chosen in the seed search.
                self.points.remove(point)
                self.points.insert(len(self.points), point)
                self.num_free_points = self.num_free_points - 1

                self.grid.add_edge(Edge(p1, point))
                self.grid.add_edge(Edge(p2, point))
                return True
        else: # Might not be trivial: Python has for/else structure...
            # If we can't keep going from this edge, remove it.
            if idx == len(possible_points)-1:
                self.grid.remove_edge(edge)
                return False
