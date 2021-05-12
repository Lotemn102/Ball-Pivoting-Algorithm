import random
import threading
import concurrent.futures
import time
from typing import List

from grid import Grid
from point import Point
from edge import Edge
from visualizer import Visualizer
import utils
import open3d as o3d
import numpy as np
import copy
from typing import Tuple


class BPA:
    def __init__(self, path, radius, visualizer=False):
        self.points = self.read_points(path) # "free points" will be on the beginning of the list, "used points" will
        # be on the end of the list.
        self.const_points = copy.deepcopy(self.points) # For visualizing
        self.radius = radius
        self.grid = Grid(points=self.points, radius=radius)
        self.num_free_points = len(self.points)
        self.visualizer = None

        if visualizer is True:
            self.visualizer = Visualizer(self.const_points)

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
                normal = [float(coordinates[3]), float(coordinates[4]), float(coordinates[5])]
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

        # Find a free point.
        p1 = self.points[0]
        p1_neighbor_points = []

        # Find all points in 2r distance from that point.
        for cell in p1.neighbor_nodes:
            p1_neighbor_points.extend(self.grid.get_cell_points(cell))

        # TODO: Don't know why it appends all points twice in the previous loop?
        p1_neighbor_points = set(p1_neighbor_points)

        # Sort points by distance from p1.
        dists = [utils.calc_distance_points(p1, p2) for p2 in p1_neighbor_points]
        p1_neighbor_points = [x for _, x in sorted(zip(dists, p1_neighbor_points))]

        # For each other point, find all points that are in 2r distance from that other point.
        for p2 in p1_neighbor_points:

            if p2.x == p1.x and p2.y == p1.y and p2.z == p1.z:
                continue

            if p2 not in self.points:
                continue

            # Find all points that are on 2r distance from p1 and p2
            intersect_cells = list(set(p1.neighbor_nodes) & set(p2.neighbor_nodes))
            possible_points = []

            for cell in intersect_cells:
                possible_points.extend(self.grid.get_cell_points(cell))

            # Sort points by distance from p2.
            dists_p2 = [utils.calc_distance_points(p2, p3) for p3 in possible_points]
            dist_p1 = [utils.calc_distance_points(p1, p3) for p3 in possible_points]
            dists = [dist_p1[i] + dists_p2[i] for i in range(len(dist_p1))]
            possible_points = [x for _, x in sorted(zip(dists, possible_points))]

            for i, p3 in enumerate(possible_points):
                if (p3.x == p1.x and p3.y == p1.y and p3.z == p1.z) or (p2.x == p3.x and p2.y == p3.y and p2.z
                                                                        == p3.z):
                    continue

                if p3 not in self.points:
                    continue

                # For each three points we got, check if a sphere with a radius of r cant be fitted inside the
                # triangle.
                if self.radius <= utils.calc_incircle_radius(p1, p2, p3):
                    # Calculate triangle's normal.
                    v1 = [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]
                    v2 = [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]
                    triangle_normal = np.cross(v1, v2)

                    # Check if the normal of the triangle is on the same direction with all 3 points normals.
                    if np.dot(triangle_normal, p1.normal) < 0:
                        continue

                    # Check if two of the points are already connected.
                    p1_and_p3_already_connected = [e for e in self.grid.edges if ((e.p1.id == p1.id)
                                                                                  and (e.p2.id == p3.id)) or (
                                                               (e.p1.id == p3.id)
                                                               and (e.p2.id == p1.id))]
                    p1_and_p2_already_connected = [e for e in self.grid.edges if ((e.p1.id == p1.id)
                                                    and (e.p2.id == p2.id)) or ((e.p1.id == p2.id)
                                                    and (e.p2.id == p1.id))]
                    p2_and_p3_already_connected = [e for e in self.grid.edges if ((e.p1.id == p2.id)
                                                    and (e.p2.id == p3.id)) or ((e.p1.id == p3.id)
                                                    and (e.p2.id == p2.id))]
                    e1 = None
                    e2 = None
                    e3 = None

                    if len(p1_and_p3_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e1 = p1_and_p3_already_connected[0]

                        if e1.num_triangles_this_edge_is_in >= 1:
                            break

                        e1.num_triangles_this_edge_is_in += 1

                    if len(p1_and_p2_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e2 = p1_and_p2_already_connected[0]

                        if e2.num_triangles_this_edge_is_in >= 1:
                            break

                        e2.num_triangles_this_edge_is_in += 1

                    if len(p2_and_p3_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e3 = p2_and_p3_already_connected[0]

                        if e3.num_triangles_this_edge_is_in >= 1:
                            break

                        e3.num_triangles_this_edge_is_in += 1

                    # Check if one of the new edges might close another triangle in the mesh.
                    are_p1_p3_closing_another_triangle_in_the_mesh = self.is_there_a_path_between_two_points(p1, p3)
                    are_p2_p3_closing_another_triangle_in_the_mesh = self.is_there_a_path_between_two_points(p2, p3)
                    are_p1_p2_closing_another_triangle_in_the_mesh = self.is_there_a_path_between_two_points(p1, p2)

                    if e1 is None:
                        e1 = Edge(p1, p3)
                        e1.num_triangles_this_edge_is_in += 1

                        if are_p1_p3_closing_another_triangle_in_the_mesh:
                            e1.num_triangles_this_edge_is_in += 1

                        self.grid.edges.append(e1)
                    if e2 is None:
                        e2 = Edge(p1, p2)
                        e2.num_triangles_this_edge_is_in += 1

                        if are_p1_p2_closing_another_triangle_in_the_mesh:
                            e2.num_triangles_this_edge_is_in += 1

                        self.grid.edges.append(e2)
                    if e3 is None:
                        e3 = Edge(p2, p3)
                        e3.num_triangles_this_edge_is_in += 1

                        if are_p2_p3_closing_another_triangle_in_the_mesh:
                            e3.num_triangles_this_edge_is_in += 1

                        self.grid.edges.append(e3)

                    self.grid.triangles.append(list({e1.p1, e1.p2, e2.p1, e2.p2, e3.p1, e3.p2}))

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

                    p1.is_used = True
                    p2.is_used = True
                    p3.is_used = True

                    return 1, (e1, e2, e3)

        # Else, find another free point and start over.
        self.points.remove(p1)
        self.points.insert(len(self.points), p1)
        self.num_free_points = self.num_free_points - 1
        return self.find_seed_triangle(), None

    def create_mesh(self, limit_iterations=float('inf')):
        times_failed_to_expand_from_new_seed = 0
        tried_to_expand_counter = 0

        while 1 and tried_to_expand_counter < limit_iterations:
            # Find a seed triangle.
            _, edges = self.find_seed_triangle()

            if edges is None:
                return

            print("new seed!")
            self.visualizer.update(edges=self.grid.edges, color='red')

            tried_to_expand_counter += 1
            i = 0

            # Try to expand from each edge.
            while i < len(edges) and tried_to_expand_counter < limit_iterations:
                e1, e2 = self.expand_triangle(edges[i], edges, False)
                tried_to_expand_counter += 1

                if e1 is not None and e2 is not None:
                    if tried_to_expand_counter >= limit_iterations:
                        self.visualizer.update(edges=self.grid.edges, color='blue')
                    else:
                        self.visualizer.update(edges=self.grid.edges, color='green')
                    edges = [e1, e2]
                    i = 0
                else:
                    i += 1

    def show_me_what_the_edge_see(self, edges, sorted_points):
        self.visualizer.close()
        pcd = o3d.geometry.PointCloud()
        points = np.array([(point.x, point.y, point.z) for point in sorted_points])
        pcd.points = o3d.utility.Vector3dVector(points)

        # Color the point in black.
        points_mask = np.zeros(shape=(len(self.const_points), 3))
        black_colors = np.zeros_like(points_mask)
        pcd.colors = o3d.Vector3dVector(black_colors)

        # Set up visualizer.
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(pcd)

        lines = []

        for edge in edges:
            lines.append([edge.p1.id, edge.p2.id])
        line_set = o3d.geometry.LineSet()
        points = np.array([(point.x, point.y, point.z) for point in sorted_points])
        line_set.points = o3d.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        vis.add_geometry(line_set)
        vis.run()

    @staticmethod
    def get_points_distances_from_edge(points, p1, p2):
        dists_p1 = [round(utils.calc_distance_points(p1, p3), 2) for p3 in points]
        dists_p2 = [round(utils.calc_distance_points(p2, p3), 2) for p3 in points]
        dists = [round(dists_p1[i] + dists_p2[i], 2) for i in range(len(dists_p1))]
        return dists

    @staticmethod
    def get_third_point_of_triangle(triangle_edges, p1, p2):
        triangle_points = []
        third_point = None

        for triangle_edge in triangle_edges:
            first_point, second_point = triangle_edge.p1, triangle_edge.p2
            triangle_points.append(first_point)
            triangle_points.append(second_point)

        triangle_points = set(triangle_points)

        for point in triangle_points:
            if point.id != p1.id and point.id != p2.id:
                third_point = point
                break

        return third_point

    def find_triangles_by_edge(self, edge):
        possible_triangles = []

        for triangle in self.grid.triangles:
            if edge.p1 in triangle and edge.p2 in triangle:
                third_point = [p for p in triangle if p.id != edge.p1.id and p.id != edge.p2.id]

                if len(third_point) > 0:
                    third_point = third_point[0]
                    possible_triangles.append([edge.p1, edge.p2, third_point])

        return possible_triangles

    def is_there_a_path_between_two_points(self, p1, p2):
        edges_first_point_int = []
        edges_second_point_int = []
        points_first_edges = []
        points_second_edges = []

        for e in self.grid.edges:
            if p1.id == e.p1.id or p1.id == e.p2.id:
                edges_first_point_int.append(e)

            if p2.id == e.p1.id or p2.id == e.p2.id:
                edges_second_point_int.append(e)

        for e in edges_first_point_int:
            points_first_edges.append(e.p1.id)
            points_first_edges.append(e.p2.id)

        for e in edges_second_point_int:
            points_second_edges.append(e.p1.id)
            points_second_edges.append(e.p2.id)

        points_first_edges = set(points_first_edges)

        if p1.id in points_first_edges:
            points_first_edges.remove(p1.id)

        points_second_edges = set(points_second_edges)

        if p2.id in points_second_edges:
            points_second_edges.remove(p2.id)

        intersection = set(points_first_edges & points_second_edges)

        return len(intersection) > 0

    @staticmethod
    def will_triangles_overlap(edge, p3, p4):
        """
        Check if a triangle defined by the 2 points of "edge" and a point p3, will overlap  a triangle defined by
        2 points of "edge" and a point p4.

        :return:
        """
        p1, p2 = edge.p1, edge.p2

        # The following section checks if p3 is the same side of the edge as the third point of the rectangle
        # we are expanding. If so - keep searching, so we won't have overlapping triangles in the mesh.
        # Calculate the normal of the triangle
        v1 = [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]
        v2 = [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]
        triangle_normal = np.cross(v1, v2)

        # Calculate the normal to the plane defined by v2 and the triangle_normal (the plane orthogonal to
        # the triangle).
        plane_normal = np.cross(v2, triangle_normal)

        # Check if p3 is in the same side of the plane as the third point.
        v3 = [p4.x - p1.x, p4.y - p1.y, p4.z - p1.z]

        return np.sign(np.dot(plane_normal, v1)) == np.sign(np.dot(plane_normal, v3))

    def expand_triangle(self, edge: Edge, edges: List[Edge], debug_flag) -> (Edge, Edge):
        if edge.num_triangles_this_edge_is_in < 2:
            # Avoid duplications.
            intersect_cells = list(set(edge.p1.neighbor_nodes) & set(edge.p2.neighbor_nodes))
            possible_points = []

            p1, p2 = edge.p1, edge.p2
            third_point_of_triangle_we_expand = self.get_third_point_of_triangle(edges, p1, p2)

            for cell in intersect_cells:
                possible_points.extend(self.grid.get_cell_points(cell))

            # Sort points by distance from p1 and p2.
            dists = self.get_points_distances_from_edge(possible_points, p1, p2)
            sorted_possible_points = [x for _, x in sorted(zip(dists, possible_points))]

            # For better performance. If we couldn't find a close point to expand to, it's better just to find new
            # seed than getting a far point.
            LIMIT_POINTS = 10
            sorted_possible_points = sorted_possible_points[:LIMIT_POINTS]

            if debug_flag:
                self.show_me_what_the_edge_see(edges, sorted_possible_points[:4])

            for index, p3 in enumerate(sorted_possible_points):
                if p3.id == p1.id or p3.id == p2.id or p3.id == third_point_of_triangle_we_expand:
                    continue

                if self.will_triangles_overlap(edge, third_point_of_triangle_we_expand, p3):
                    continue

                # If a sphere's radius is smaller than the radius of the incircle of a triangle, the sphere can fit into
                # the triangle.
                if self.radius <= utils.calc_incircle_radius(p1, p2, p3):
                    # Calculate new triangle's normal.
                    v1 = [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]
                    v2 = [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]
                    new_triangle_normal = np.cross(v1, v2)

                    # Check if the normal of the triangle is on the same direction with other points normals.
                    if np.dot(new_triangle_normal, p1.normal) < 0 and np.dot(new_triangle_normal, p2.normal) < 0:
                        continue

                    e1 = None
                    e2 = None

                    p1_and_p3_already_connected = [e for e in self.grid.edges if ((e.p1.id == p1.id)
                                                       and (e.p2.id == p3.id)) or ((e.p1.id == p3.id)
                                                       and (e.p2.id == p1.id))]
                    p2_and_p3_already_connected = [e for e in self.grid.edges if ((e.p1.id == p2.id)
                                                       and (e.p2.id == p3.id)) or ((e.p1.id == p3.id)
                                                       and (e.p2.id == p2.id))]

                    # These points are already part of a triangle!
                    if len(p1_and_p3_already_connected) and len(p2_and_p3_already_connected):
                        continue

                    if len(p1_and_p3_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e1 = p1_and_p3_already_connected[0]

                        if e1.num_triangles_this_edge_is_in >= 2:
                            continue

                        # Make sure that if the edge they are already connected with is part of the triangle, the new
                        # triangle will not overlap
                        # TODO: Continue this part
                        '''
                        triangles = self.find_triangles_by_edge(e1)

                        if len(triangles) >= 2:
                            continue
                        else:
                            third_point_of_triangle = [p for p in triangles[0] if p.id != p1.id and p.id != p3.id][0]
                            if self.will_triangles_overlap(e1, third_point_of_triangle, p2):
                                continue
                        '''

                        e1.num_triangles_this_edge_is_in += 1

                    if len(p2_and_p3_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e2 = p2_and_p3_already_connected[0]

                        if e2.num_triangles_this_edge_is_in >= 2:
                            continue

                        e2.num_triangles_this_edge_is_in += 1

                    # Check if one of the new edges might close another triangle in the mesh.
                    are_p1_p3_closing_another_triangle_in_the_mesh = False
                    are_p2_p3_closing_another_triangle_in_the_mesh = False

                    if p3.is_used:
                        are_p1_p3_closing_another_triangle_in_the_mesh = self.is_there_a_path_between_two_points(p1, p3)
                        are_p2_p3_closing_another_triangle_in_the_mesh = self.is_there_a_path_between_two_points(p2, p3)

                    # Update that the edge we expand is now part of the triangle.
                    edge.num_triangles_this_edge_is_in += 1

                    # Update that 'point' is not free anymore, so it won't be accidentally chosen in the seed search.
                    p3.is_used = True

                    if e1 is None:
                        e1 = Edge(p1, p3)
                        e1.num_triangles_this_edge_is_in += 1

                        if are_p1_p3_closing_another_triangle_in_the_mesh:
                            e1.num_triangles_this_edge_is_in += 1
                            pass

                        self.grid.add_edge(e1)
                    if e2 is None:
                        e2 = Edge(p2, p3)
                        e2.num_triangles_this_edge_is_in += 1

                        if are_p2_p3_closing_another_triangle_in_the_mesh:
                            e2.num_triangles_this_edge_is_in += 1
                            pass

                        self.grid.add_edge(e2)

                    self.grid.triangles.append(list({e1.p1, e1.p2, e2.p1, e2.p2, edge.p1, edge.p2}))
                    return e1, e2
            else:
                return None, None

        return None, None
