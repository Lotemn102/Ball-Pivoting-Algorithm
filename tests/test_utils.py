import unittest
from utils import calc_distance_points, calc_incircle_radius, calc_distance_point_to_edge, encode_cell, decode_cell
from point import Point
from edge import Edge


class TestUtils(unittest.TestCase):
    def test_distance(self):
        p1 = Point(1, 1, 0, id=0)
        p2 = Point(2, 1, 2, id=0)
        d = calc_distance_points(p1, p2)
        self.assertEqual(round(d, 2), 2.24)

        p3 = Point(0, 0, 0, id=0)
        p4 = Point(-1, 1, 2, id=0)
        d = calc_distance_points(p3, p4)
        self.assertEqual(round(d, 2), 2.45)

    def test_incircle_radius(self):
        p1 = Point(1, 1, 1, id=0)
        p2 = Point(0, 2, 0, id=0)
        p3 = Point(3, 3, 3, id=0)

        r = calc_incircle_radius(p1, p2, p3)
        self.assertEqual(round(r, 3), 0.592)
        p1 = Point(1, 1, 1, id=0)
        p2 = Point(0, -1, 0, id=0)
        p3 = Point(2, -1, 3, id=0)

        r = calc_incircle_radius(p1, p2, p3)
        self.assertEqual(round(r, 3), 0.804)

    def test_calc_distance_edge_to_point(self):
        p1 = Point(0, 0, 0, id=0)
        p2 = Point(0, 1, 0, id=0)
        p3 = Point(1, 0, 0, id=0)
        p4 = Point(1, 1, 0, id=0)

        e1 = Edge(p1, p2)
        e2 = Edge(p1, p3)
        e3 = Edge(p2, p3)

        d1 = calc_distance_point_to_edge(p4, e1)
        d2 = calc_distance_point_to_edge(p4, e2)
        d3 = calc_distance_point_to_edge(p4, e3)

        self.assertEqual(d1, 1.0)
        self.assertEqual(d2, 1.0)

    def test_encoding_decoding(self):
        x = 1
        y = 2
        z = 3

        code = encode_cell(x, y, z)
        x, y, z = decode_cell(code)

        self.assertEqual(x, 1)
        self.assertEqual(y, 2)
        self.assertEqual(z, 3)





