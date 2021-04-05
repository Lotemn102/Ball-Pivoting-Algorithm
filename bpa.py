from grid import Grid, Point
import math


class BPA:
    def __init__(self, path, radius):
        pass
        #points = self._read_points(path)
        #self.grid = Grid(points=points, radius=radius)

    @staticmethod
    def _read_points(path):
        points = []
        f = open(path, "r")
        lines = f.read().splitlines()

        for line in lines:
            coordinates = line.split()

            if len(coordinates) is not 3:
                continue

            p = Point(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]))
            points.append(p)

        return points

    @staticmethod
    def calc_incircle_radius(p1: Point, p2: Point, p3: Point):
        """
        Calculate the radius of the incircle in a triangle.
        Based on this formula:
         https://en.wikipedia.org/wiki/Incircle_and_excircles_of_a_triangle#Radius

        :param p1: First point of triangle.
        :param p2: Second point of triangle.
        :param p3: Third point of triangle.
        :return: The radius of the incircle.
        """

        edge_1_length = BPA.calc_distance(p1, p2)
        edge_2_length = BPA.calc_distance(p2, p3)
        edge_3_length = BPA.calc_distance(p1, p3)

        s = (edge_1_length + edge_2_length + edge_3_length) / 2
        r = math.sqrt(((s - edge_1_length)*(s - edge_2_length)*(s - edge_3_length)) / s)
        return r

    @staticmethod
    def calc_distance(p1: Point, p2: Point):
        """
        Calculate the distance between 2 3D points.

        :param p1: First point.
        :param p2: Second point.
        :return: Distance between the points.
        """
        return math.sqrt(math.pow((p2.x - p1.x), 2) + math.pow((p2.y - p1.y), 2) + math.pow((p2.z - p1.z), 2))

    def _find_seed_triangle(self):
        pass

    def create_mesh(self):
        pass



bpa = BPA('bunny.pcd', 0.5)
