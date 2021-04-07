import unittest
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

from grid import Grid
from point import Point
from bpa import BPA


class TestBPA(unittest.TestCase):
    '''
    def test_create_test_file(self):
        f = open("test_1_no_normal.txt", "w")

        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    point_as_string = str(i + 1) + " " + str(j + 1) + " " + str(k + 1) + "\n"
                    f.write(point_as_string)

        f.close()
    '''

    def test_find_seed_1(self):
        # Load data.
        bpa = BPA(path='test_1_no_normal.txt', radius=0.5)

        # Find a single triangle.
        bpa.find_seed_triangle()
        edges = bpa.grid.edges
        x_vals = []
        y_vals = []
        z_vals = []

        for edge in edges:
            x_vals.append(edge.p1.x)
            x_vals.append(edge.p2.x)
            y_vals.append(edge.p1.y)
            y_vals.append(edge.p2.y)
            z_vals.append(edge.p1.z)
            z_vals.append(edge.p2.z)

        fig = pyplot.figure()
        ax = Axes3D(fig)
        pyplot.plot(x_vals, y_vals, z_vals)
        pyplot.show()

    def test_find_seed_2(self):
        # Load data.
        bpa = BPA(path='test_1_no_normal.txt', radius=0.5)

        # Find a mulitple triangle.
        for i in range(50):
            res = bpa.find_seed_triangle()

            # There only 27 points, so max number of seed triangles is 9
            if i > 9:
                self.assertEqual(res, -1)

        edges = bpa.grid.edges
        x_vals = []
        y_vals = []
        z_vals = []

        for edge in edges:
            x_vals.append(edge.p1.x)
            x_vals.append(edge.p2.x)
            y_vals.append(edge.p1.y)
            y_vals.append(edge.p2.y)
            z_vals.append(edge.p1.z)
            z_vals.append(edge.p2.z)

        fig = pyplot.figure()
        ax = Axes3D(fig)
        pyplot.plot(x_vals, y_vals, z_vals)
        # For sanity check
        pyplot.show()

    def test_expand_triangle(self):
        # Load data.
        bpa = BPA(path='test_1_no_normal.txt', radius=0.2)
        bpa.grid.show()

        # Find a seed triangle.
        bpa.find_seed_triangle()

        # Expand the seed triangle.
        edges = bpa.grid.edges
        bpa.expand_triangle(edges[0])

        print(bpa.grid.edges)










