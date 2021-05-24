import unittest
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

from grid import Grid
from point import Point
from bpa import BPA
import open3d as o3d
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

        # Find a mulitiple triangle.
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

    def test_calc_normals(self):
        # Load data.
        bpa = BPA(path='normals_test.txt', radius=0.2, visualizer=True)

        # Find a seed triangle.
        bpa.find_seed_triangle()
        bpa.visualizer.update(edges=bpa.grid.edges, color='red')
        bpa.visualizer.lock()

    def test_create_mesh(self):
        # Load data.
        bpa = BPA(path='large_bunny_with_normals.txt', radius=0.005, visualizer=True)
        bpa.create_mesh(limit_iterations=1000)
        bpa.visualizer.lock()

    def test_small_bunny(self):
        # Load data.
        bpa = BPA(path='bunny_with_normals.txt', radius=0.0005, visualizer=True)
        bpa.create_mesh(limit_iterations=900)
        bpa.visualizer.lock()

    def test_tea(self):
        # Load data.
        bpa = BPA(path='teapot_with_normal.txt', radius=0.02, visualizer=True)
        print("Starting...")
        bpa.create_mesh(limit_iterations=1000)
        print("Finished.")
        bpa.visualizer.lock()

    def test_multi_process(self):
        # Load data.
        # TODO: Check why this runs very slow? maybe pass limit_iterations to find_seed?
        bpa = BPA(path='bunny_with_normals.txt', radius=0.0005, visualizer=True, num_workers=1)
        bpa.create_mesh_thread(limit_iterations=1000)
        bpa.visualizer.lock()

















