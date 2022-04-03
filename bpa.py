from typing import List, Tuple
from tqdm import tqdm
import numpy as np

from grid import Grid
from point import Point
from edge import Edge
from visualizer import Visualizer
import utils

INFINITY = np.inf

class BPA:
    def __init__(self, path, radius, visualizer=False, num_workers=1):
        self.first_free_point_index = 0
        self.num_points_i_tried_to_seed_from = 0
        self.points = self.read_points(path)
        self.radius = radius
        self.grid = Grid(points=self.points, radius=radius)
        self.num_free_points = len(self.points)
        self.visualizer = None
        self.num_workers = num_workers

        if visualizer is True:
            self.visualizer = Visualizer(self.points)

    def read_points(self, path: str) -> List:
        """
        Read the points from a text file.

        :param path: The path to the text file.
        :return: A list with the points.
        """
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

    @staticmethod
    def get_points_distances_from_edge(points: List, p1: Point, p2: Point) -> list:
        """
        Calculate points distance from an edge defined by p1 and p2. The heuristic for the distance is the summation of
        euclidean distance between p1 and p, and p2 and p.

        :param points: List of points to check.
        :param p1: First point define the edge.
        :param p2: Second point define the edge.
        :return: The distances.
        """
        dists_p1 = [round(utils.calc_distance_points(p1, p3), 2) for p3 in points]
        dists_p2 = [round(utils.calc_distance_points(p2, p3), 2) for p3 in points]
        dists = [round(dists_p1[i] + dists_p2[i], 2) for i in range(len(dists_p1))]
        return dists

    @staticmethod
    def get_third_point_of_triangle(triangle_edges: List, p1: Point, p2: Point) -> Point:
        """
        Given a triangle's edges, and 2 of the points of the triangle, find the thirds point.

        :param triangle_edges: List of the edges.
        :param p1: First point.
        :param p2: Second point.
        :return: The third point.
        """
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

    @staticmethod
    def will_triangles_overlap(edge: Edge, p3: Point, p4: Point) -> bool:
        """
        Check if a triangle defined by the 2 points of "edge" and a point p3, will overlap  a triangle defined by
        2 points of "edge" and a point p4.

        :return: Boolean.
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

    def create_mesh(self,  limit_iterations: int = INFINITY, first_point_index: int = 0):
        """
        Create mesh from the points.

        :param limit_iterations: (Optional) number of iterations to limit the algorithm's run.
        :param first_point_index: First index the algorithm will try to find seed triangle from.
        :return: None
        """
        tried_to_expand_counter = 0

        with tqdm(total=limit_iterations) as pbar:
            while 1 and tried_to_expand_counter < limit_iterations:
                # Find a seed triangle.
                _, edges, last_point_index = self.find_seed_triangle(first_point_index=first_point_index)
                first_point_index = last_point_index

                if edges is None or edges is -1:
                    return

                if self.visualizer is not None:
                    self.visualizer.update(edges=self.grid.edges, grid_triangles=self.grid.triangles, color='red')

                tried_to_expand_counter += 1
                pbar.update(1)
                i = 0

                # Try to expand from each edge.
                while i < len(edges) and tried_to_expand_counter < limit_iterations:
                    e1, e2 = self.expand_triangle(edges[i], edges)
                    tried_to_expand_counter += 1
                    pbar.update(1)

                    if e1 is not None and e2 is not None:
                        edges = [e1, e2]
                        i = 0

                        if self.visualizer is not None:
                            if tried_to_expand_counter >= limit_iterations:
                                self.visualizer.update(edges=self.grid.edges, grid_triangles=self.grid.triangles,
                                                       color='blue')
                            else:
                                self.visualizer.update(edges=self.grid.edges, grid_triangles=self.grid.triangles,
                                                       color='green')
                    else:
                        i += 1

    def find_seed_triangle(self, first_point_index=0, num_recursion_calls=0) -> (int, Tuple):
        """
        Find seed triangle.

        :param first_point_index: First index the algorithm will try to find seed triangle from.
        :param num_recursion_calls: Number of recursion calls for the recursion stop condition. You should not pass to
        this function anything beside 0 in this parameter.
        :return: None.
        """
        if num_recursion_calls > len(self.points):
            print("i was here")
            return -1, -1, -1

        # Find a free point.
        #while first_point_index < len(self.points)-1 and self.points[first_point_index].is_used:
        #    first_point_index += 1

        if first_point_index >= len(self.points) - 1:
            first_point_index = 0

        p1 = self.points[first_point_index]
        p1_neighbor_points = []

        # Find all points in 2r distance from that point.
        for cell in p1.neighbor_nodes:
            p1_neighbor_points.extend(self.grid.get_cell_points(cell))

        # TODO: Don't know why it appends all points twice in the previous loop?
        p1_neighbor_points = set(p1_neighbor_points)

        # Sort points by distance from p1.
        dists = [utils.calc_distance_points(p1, p2) for p2 in p1_neighbor_points]
        p1_neighbor_points = [x for _, x in sorted(zip(dists, p1_neighbor_points))]

        # For better performance. If we couldn't find a close point to expand to, it's better just to find new
        # seed than getting a far point.
        LIMIT_POINTS = 6
        p1_neighbor_points = p1_neighbor_points[:LIMIT_POINTS]

        # For each other point, find all points that are in 2r distance from that other point.
        for p2 in p1_neighbor_points:
            if p2.is_used:
                #continue
                pass

            if p2.x == p1.x and p2.y == p1.y and p2.z == p1.z:
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

            # For better performance. If we couldn't find a close point to expand to, it's better just to find new
            # seed than getting a far point.
            LIMIT_POINTS = 5
            possible_points = possible_points[:LIMIT_POINTS]

            for i, p3 in enumerate(possible_points):
                if p3.is_used:
                    #continue
                    pass

                if (p3.x == p1.x and p3.y == p1.y and p3.z == p1.z) or (p2.x == p3.x and p2.y == p3.y and p2.z
                                                                        == p3.z):
                    continue

                # For each three points we got, check if a sphere with a radius of r cant be fitted inside the
                # triangle.
                if self.radius <= utils.calc_incircle_radius(p1, p2, p3):
                    # Calculate triangle's normal.
                    v1 = [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]
                    v2 = [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]
                    triangle_normal = np.cross(v1, v2)

                    # Check if the normal of the triangle is on the same direction with points normals.
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

                    if len(p1_and_p3_already_connected) > 0 or len(p1_and_p2_already_connected) > 0 or\
                            len(p2_and_p3_already_connected) > 0:
                        continue

                    # Check if one of the new edges might close another triangle in the mesh.
                    are_p1_p3_closing_another_triangle_in_the_mesh = \
                        self.is_there_a_path_between_two_points(p1, p3, point_of_triangle_we_creating=p2)
                    are_p2_p3_closing_another_triangle_in_the_mesh = \
                        self.is_there_a_path_between_two_points(p2, p3, point_of_triangle_we_creating=p1)
                    are_p1_p2_closing_another_triangle_in_the_mesh = \
                        self.is_there_a_path_between_two_points(p1, p2, point_of_triangle_we_creating=p3)

                    if e1 is None:
                        e1 = Edge(p1, p3)
                        e1.num_triangles_this_edge_is_in += 1

                        if are_p1_p3_closing_another_triangle_in_the_mesh:
                            e1.num_triangles_this_edge_is_in += 1

                    if e2 is None:
                        e2 = Edge(p1, p2)
                        e2.num_triangles_this_edge_is_in += 1

                        if are_p1_p2_closing_another_triangle_in_the_mesh:
                            e2.num_triangles_this_edge_is_in += 1

                    if e3 is None:
                        e3 = Edge(p2, p3)
                        e3.num_triangles_this_edge_is_in += 1

                        if are_p2_p3_closing_another_triangle_in_the_mesh:
                            e3.num_triangles_this_edge_is_in += 1

                    # Get rid of these extreme acute or obtuse triangles.
                    min_angle, max_angle = utils.calc_min_max_angle_of_triangle(e1, e2, e3)
                    if max_angle > 170 or min_angle < 20:
                        continue

                    self.grid.edges.append(e1)
                    self.grid.edges.append(e2)
                    self.grid.edges.append(e3)

                    triangle = sorted(list({e1.p1, e1.p2, e2.p1, e2.p2, e3.p1, e3.p2}))
                    self.grid.triangles.append(triangle)

                    # Move the points to the end of the list.
                    self.first_free_point_index += 1

                    p1.is_used = True
                    p2.is_used = True
                    p3.is_used = True

                    return 1, (e1, e2, e3), first_point_index

        # Else, find another free point and start over.
        return self.find_seed_triangle(first_point_index=first_point_index+1, num_recursion_calls=num_recursion_calls+1)

    def expand_triangle(self, edge: Edge, triangle_edges: List[Edge]) -> (Edge, Edge):
        """
        Expand a triangle from an edge.

        :param edge: The edge we are expanding.
        :param triangle_edges: All edges of the triangle we are expanding.
        :return: Tuple of two edges of the new formed triangle.
        """
        if edge.num_triangles_this_edge_is_in < 2:
            # Avoid duplications.
            intersect_cells = list(set(edge.p1.neighbor_nodes) & set(edge.p2.neighbor_nodes))
            possible_points = []

            p1, p2 = edge.p1, edge.p2
            third_point_of_triangle_we_expand = self.get_third_point_of_triangle(triangle_edges, p1, p2)

            for cell in intersect_cells:
                possible_points.extend(self.grid.get_cell_points(cell))

            # Sort points by distance from p1 and p2.
            dists = self.get_points_distances_from_edge(possible_points, p1, p2)
            sorted_possible_points = [x for _, x in sorted(zip(dists, possible_points))]

            # For better performance. If we couldn't find a close point to expand to, it's better just to find new
            # seed than getting a far point.
            LIMIT_POINTS = 5
            sorted_possible_points = sorted_possible_points[:LIMIT_POINTS]

            for index, p3 in enumerate(sorted_possible_points):
                if p3.id == p1.id or p3.id == p2.id or p3.id == third_point_of_triangle_we_expand.id:
                    continue

                if self.will_triangles_overlap(edge, third_point_of_triangle_we_expand, p3):
                    continue

                # If a sphere's radius is smaller than the radius of the incircle of a triangle, the sphere can fit into
                # the triangle.
                t = utils.calc_incircle_radius(p1, p2, p3)
                if self.radius <= utils.calc_incircle_radius(p1, p2, p3):
                    # Calculate new triangle's normal.
                    v1 = [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]
                    v2 = [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]
                    new_triangle_normal = np.cross(v1, v2)

                    # Check if the normal of the triangle is on the same direction with other points normals.
                    if np.dot(new_triangle_normal, p1.normal) < 0 and np.dot(new_triangle_normal, p2.normal) < 0:
                        # TODO: Fix this! need to check if the vertices order is anti-clockwise, and if so, change the
                        #  vector order.
                        pass

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
                        triangles = self.find_triangles_by_edge(e1)

                        if len(triangles) >= 2:
                            continue
                        else:
                            third_point_of_triangle = [p for p in triangles[0] if p.id != p1.id and p.id != p3.id][0]

                            if self.will_triangles_overlap(e1, third_point_of_triangle, p2):
                                continue

                        e1.num_triangles_this_edge_is_in += 1

                    if len(p2_and_p3_already_connected) > 0:
                        # Find the single edge they are connected with.
                        e2 = p2_and_p3_already_connected[0]

                        if e2.num_triangles_this_edge_is_in >= 2:
                            continue

                        # Make sure that if the edge they are already connected with is part of the triangle, the new
                        # triangle will not overlap
                        triangles = self.find_triangles_by_edge(e2)

                        if len(triangles) >= 2:
                            continue
                        else:
                            third_point_of_triangle = [p for p in triangles[0] if p.id != p1.id and p.id != p3.id][0]
                            if self.will_triangles_overlap(e2, third_point_of_triangle, p1):
                                continue

                        e2.num_triangles_this_edge_is_in += 1

                    # Check if one of the new edges might close another triangle in the mesh.
                    are_p1_p3_closing_another_triangle_in_the_mesh = False
                    are_p2_p3_closing_another_triangle_in_the_mesh = False

                    if p3.is_used:
                        are_p1_p3_closing_another_triangle_in_the_mesh = self.is_there_a_path_between_two_points(p1, p3, p2)
                        are_p2_p3_closing_another_triangle_in_the_mesh = self.is_there_a_path_between_two_points(p2, p3, p1)

                    # Update that the edge we expand is now part of the triangle.
                    edge.num_triangles_this_edge_is_in += 1

                    # Update that 'point' is not free anymore, so it won't be accidentally chosen in the seed search.
                    p3.is_used = True

                    if e1 is None:
                        e1 = Edge(p1, p3)
                        e1.num_triangles_this_edge_is_in += 1

                        if are_p1_p3_closing_another_triangle_in_the_mesh:
                            e1.num_triangles_this_edge_is_in += 1

                    if e2 is None:
                        e2 = Edge(p2, p3)
                        e2.num_triangles_this_edge_is_in += 1

                        if are_p2_p3_closing_another_triangle_in_the_mesh:
                            e2.num_triangles_this_edge_is_in += 1

                    # Get rid of these extreme acute or obtuse triangles.
                    min_angle, max_angle = utils.calc_min_max_angle_of_triangle(e1, e2, edge)
                    if max_angle > 180 or min_angle < 1:
                        continue

                    self.grid.add_edge(e1)
                    self.grid.add_edge(e2)

                    triangle = sorted(list({e1.p1, e1.p2, e2.p1, e2.p2,edge.p1, edge.p2}))

                    v1 = [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]
                    v2 = [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]
                    normal = np.cross(v1, v2)

                    if np.sign(np.dot(normal, p1.normal)) < 0:
                        triangle.reverse()

                    self.grid.triangles.append(triangle)
                    return e1, e2
            else:
                return None, None

        return None, None

    def find_triangles_by_edge(self, edge: Edge) -> List:
        """
        Find all triangles the edge is in them.

        :param edge: The edge we are looking at.
        :return: List of the triangles this edge is in them.
        """
        possible_triangles = []

        for triangle in self.grid.triangles:
            if edge.p1 in triangle and edge.p2 in triangle:
                third_point = [p for p in triangle if p.id != edge.p1.id and p.id != edge.p2.id]

                if len(third_point) > 0:
                    third_point = third_point[0]
                    possible_triangles.append([edge.p1, edge.p2, third_point])

        return possible_triangles

    def is_there_a_path_between_two_points(self, p1, p2, point_of_triangle_we_creating):
        """
        Check if there is a path between two gicen points.

        :param p1: First point we check.
        :param p2: Second point we check.
        :param point_of_triangle_we_creating: Third point of a triangle these 2 points are in.
        :return:
        """
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
        if point_of_triangle_we_creating.id in intersection:
            # I already know these two points have a path, because they are part of a triangle. Remove that third point
            # to find out if there are multiple routes between the points.
            intersection.remove(point_of_triangle_we_creating.id)

        return len(intersection) > 0

