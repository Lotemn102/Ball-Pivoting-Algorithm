import unittest
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

from grid import Grid
from point import Point
from bpa import BPA
import open3d
import numpy as np
import time


class TestBPA(unittest.TestCase):
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
        bpa = BPA(path='bunny_with_normals.txt', radius=0.002, visualizer=True)

        # Find a seed triangle.
        bpa.find_seed_triangle()

        # Expand the seed triangle.
        edges = bpa.grid.edges
        bpa.expand_triangle(edges[0])

        self.assertEqual(len(bpa.grid.edges), 5)

    def test_visualizer(self):
        # Load data.
        bpa = BPA(path='bunny_with_normals.txt', radius=0.002, visualizer=True)
        edge_index = 0

        while 1:
            # Find a seed triangle.
            bpa.find_seed_triangle()
            bpa.update_visualizer(color='red')

            # Expand the seed triangle.
            edges = bpa.grid.edges

            while bpa.expand_triangle(edges[edge_index]):
                edges = bpa.grid.edges
                bpa.update_visualizer(color='green')
                edge_index += 1












