import random
import threading
import concurrent.futures
import time
from typing import List

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
    '''
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

        for edge in self.grid.edges:
            if edge.color == []:
                edge.color = c

        colors = [edge.color for edge in self.grid.edges]
        line_set = o3d.geometry.LineSet()
        points = np.array([(point.x, point.y, point.z) for point in self.const_points])
        line_set.points = o3d.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)

        self.vis.add_geometry(line_set)
        self.vis.update_geometry()
        self.vis.poll_events()
        self.vis.update_renderer()
    '''

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

        '''
        triangles = []

        for triangle in self.grid.triangles:
            index_1 = self.points.index(triangle[0])
            index_2 = self.points.index(triangle[1])
            index_3 = self.points.index(triangle[2])
            triangles.append([index_1, index_2, index_3])
        '''

        lines = [[edge.p1.id, edge.p2.id] for edge in self.grid.edges]

        for edge in self.grid.edges:
            if edge.color == []:
                edge.color = c

        colors = [edge.color for edge in self.grid.edges]
        line_set = o3d.geometry.LineSet()
        points = np.array([(point.x, point.y, point.z) for point in self.const_points])
        line_set.points = o3d.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)

        '''
        triangles = np.asarray(triangles).astype(np.int32)
        points = np.array([(point.x, point.y, point.z) for point in self.points])

        mesh = o3d.TriangleMesh()
        mesh.vertices = o3d.Vector3dVector(points)
        mesh.triangles = o3d.Vector3iVector(np.array(triangles))
        #mesh.paint_uniform_color(c)
        #self.vis.add_geometry(mesh)
        '''

        self.vis.get_render_option().point_size = 3.5
        self.vis.add_geometry(line_set)
        self.vis.update_geometry()
        self.vis.poll_events()
        self.vis.update_renderer()

    def lock_visualizer(self):
        self.vis.run()

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

        # TODO: Don't know why i append all points twice in the previous loop?
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
                    v2 = [p1.x - p3.x, p1.y - p3.y, p1.z - p3.z]
                    triangle_normal = np.cross(v1, v2)

                    # Check if the normal of the triangle is on the same direction with all 3 points normals.
                    if np.dot(triangle_normal, p1.normal) < 0 or np.dot(triangle_normal, p2.normal) < 0 or \
                        np.dot(triangle_normal, p3.normal) < 0:
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
                    if len(p1_and_p2_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e2 = p1_and_p3_already_connected[0]
                    if len(p2_and_p3_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e3 = p2_and_p3_already_connected[0]

                    if e1 is None:
                        e1 = Edge(p1, p3)
                    if e2 is None:
                        e2 = Edge(p1, p2)
                    if e3 is None:
                        e3 = Edge(p2, p3)

                    e1.num_triangles_this_edge_is_in += 1
                    e2.num_triangles_this_edge_is_in += 1
                    e3.num_triangles_this_edge_is_in += 1

                    self.grid.edges.append(e1)
                    self.grid.edges.append(e2)
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
            if times_failed_to_expand_from_new_seed > 2:
                return

            # Find a seed triangle.
            _, edges = self.find_seed_triangle()
            print("new seed!")
            self.update_visualizer(color='red')

            # Try to expand from each edge.
            while edges and tried_to_expand_counter < limit_iterations:
                tried_to_expand_counter += 1
                i = 0

                while i < len(edges) and tried_to_expand_counter < limit_iterations:
                    e1, e2 = self.expand_triangle(edges[i], edges)

                    if e1 is not None and e2 is not None:
                        self.update_visualizer(color='green')
                        edges = [e1, e2]
                        #i = 0
                    else:
                        i += 1
                        tried_to_expand_counter += 1
                        continue
            else:
                times_failed_to_expand_from_new_seed += 1

    def show_me_what_the_edge_see(self, edge, sorted_points):
        self.vis.close()
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

        lines = [[edge.p1.id, edge.p2.id]]
        line_set = o3d.geometry.LineSet()
        points = np.array([(point.x, point.y, point.z) for point in sorted_points])
        line_set.points = o3d.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        vis.add_geometry(line_set)
        vis.run()

    def expand_triangle(self, edge: Edge, edges: List[Edge]) -> (Edge, Edge):
        if edge.num_triangles_this_edge_is_in < 2:
            # Avoid duplications.
            intersect_cells = list(set(edge.p1.neighbor_nodes) & set(edge.p2.neighbor_nodes))
            possible_points = []

            p1, p2 = edge.p1, edge.p2

            for cell in intersect_cells:
                possible_points.extend(self.grid.get_cell_points(cell))

            # Sort points by distance from p1 and p2.
            dists_p1 = [utils.calc_distance_points(p1, p3) for p3 in possible_points]
            dists_p2 = [utils.calc_distance_points(p2, p3) for p3 in possible_points]
            dists = [dists_p1[i] + dists_p2[i] for i in range(len(dists_p1))]

            sorted_possible_points = [x for _, x in sorted(zip(dists, possible_points))]
            self.show_me_what_the_edge_see(edge, sorted_possible_points[:6])

            for index, p3 in enumerate(sorted_possible_points):
                if p3.id == p1.id or p3.id == p2.id:
                    continue

                if p3 not in self.points:
                    continue

                # Is there an edge in the triangle i'm expanding that is closer to the closest point i've found? If so,
                # this triangle might cause intersection.

                is_there_a_closer_edge_to_p3 = False

                for triangle_edge in edges:
                    if utils.calc_distance_point_to_edge(point=sorted_possible_points[index],
                                                         edge=triangle_edge) < utils. \
                            calc_distance_point_to_edge(point=sorted_possible_points[index], edge=edge):
                        is_there_a_closer_edge_to_p3 = True
                        break

                if is_there_a_closer_edge_to_p3:
                    continue

                # If a sphere's radius is smaller than the radius of the incircle of a triangle, the sphere can fit into
                # the triangle.
                if self.radius <= utils.calc_incircle_radius(p1, p2, p3):
                    # Calculate triangle's normal.
                    v1 = [p1.x - p2.x, p1.y - p2.y, p1.z - p2.z]
                    v2 = [p1.x - p3.x, p1.y - p3.y, p1.z - p3.z]
                    triangle_normal = np.cross(v1, v2)

                    # Check if the normal of the triangle is on the same direction with all 3 points normals.
                    if np.dot(triangle_normal, p1.normal) < 0 or np.dot(triangle_normal, p2.normal) < 0 or \
                            np.dot(triangle_normal, p3.normal) < 0:
                        continue

                    # Update that 'point' is not free anymore, so it won't be accidentally chosen in the seed search.
                    p3.is_used = True

                    p1_and_p3_already_connected = [e for e in self.grid.edges if ((e.p1.id == p1.id)
                                                       and (e.p2.id == p3.id)) or ((e.p1.id == p3.id)
                                                       and (e.p2.id == p1.id))]
                    p2_and_p3_already_connected = [e for e in self.grid.edges if ((e.p1.id == p2.id)
                                                       and (e.p2.id == p3.id)) or ((e.p1.id == p3.id)
                                                       and (e.p2.id == p2.id))]
                    e1 = None
                    e2 = None

                    # These points are already part of a triangle!
                    if len(p1_and_p3_already_connected) and len(p2_and_p3_already_connected):
                        continue

                    if len(p1_and_p3_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e1 = p1_and_p3_already_connected[0]
                        e1.num_triangles_this_edge_is_in += 1
                    if len(p2_and_p3_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e2 = p2_and_p3_already_connected[0]
                        e2.num_triangles_this_edge_is_in += 1

                    edge.num_triangles_this_edge_is_in += 1

                    if e1 is None:
                        e1 = Edge(p1, p3)
                    if e2 is None:
                        e2 = Edge(p2, p3)

                    self.grid.add_edge(e1)
                    self.grid.add_edge(e2)
                    self.grid.triangles.append(list({e1.p1, e1.p2, e2.p1, e2.p2, edge.p1, edge.p2}))
                    return e1, e2
        # If we can't keep going from this edge, remove it.
        else:
            return None, None
