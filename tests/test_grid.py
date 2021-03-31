import unittest
from grid import Grid, Point


class TestGrid(unittest.TestCase):
    def test_create_grid(self):
        points = []

        for i in range(1000):
            p = Point(i, i, i)
            points.append(p)

        grid1 = Grid(radius=1)
        grid1.init_with_data(points)
        self.assertEqual(len(grid1.cells), 500)

        grid2 = Grid(radius=0.5)
        grid2.init_with_data(points)
        self.assertEqual(len(grid2.cells), 1000)

    def test_get_neighbors(self):
        points = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    p = Point(i+1, j+1, k+1)
                    points.append(p)

        grid = Grid(radius=0.5)
        grid.init_with_data(points)

        neighbor_points = grid.get_neighbor_points(points[0])
        self.assertLessEqual(len(neighbor_points), 27)

        points_vals = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]

        for point in neighbor_points:
            coordinates = (point.x, point.y, point.z)
            self.assertIn(coordinates, points_vals)

        grid.show()










