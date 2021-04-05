import unittest

from utils import calc_distance, calc_incircle_radius
from point import Point


class TestUtils(unittest.TestCase):
    def test_distance(self):
        p1 = Point(1, 1, 0)
        p2 = Point(2, 1, 2)
        d = calc_distance(p1, p2)
        self.assertEqual(round(d, 2), 2.24)

        p3 = Point(0, 0, 0)
        p4 = Point(-1, 1, 2)
        d = calc_distance(p3, p4)
        self.assertEqual(round(d, 2), 2.45)

    def test_incircle_radius(self):
        p1 = Point(1, 1, 1)
        p2 = Point(0, 2, 0)
        p3 = Point(3, 3, 3)

        r = calc_incircle_radius(p1, p2, p3)
        self.assertEqual(round(r, 3), 0.592)

        p1 = Point(1, 1, 1)
        p2 = Point(0, -1, 0)
        p3 = Point(2, -1, 3)

        r = calc_incircle_radius(p1, p2, p3)
        self.assertEqual(round(r, 3), 0.804)



