import unittest
from octree import Octree, Point


class TesOctree(unittest.TestCase):
    def test_tree(self):
        test_tree = Octree(radius=1, length=5)
        test_tree.insert((1, 2, 3))

