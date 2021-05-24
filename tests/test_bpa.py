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
        bpa = BPA(path='../data/bunny_with_normals.txt', radius=0.0005, visualizer=True, num_workers=3)
        bpa.create_mesh(limit_iterations=1000)
        bpa.visualizer.lock()

    def test_medium_bunny(self):
        # Load data.
        bpa = BPA(path='../data/bunny_with_normals.txt', radius=0.0005, visualizer=True, num_workers=1)
        bpa.create_mesh()
        bpa.visualizer.lock()

    def test_normal_drawing(self):
        bpa = BPA(path='../data/large_bunny_with_normals.txt', radius=0.0005, visualizer=True, num_workers=1)
        bpa.visualizer.draw_with_normals(normals_size=0.5)

















