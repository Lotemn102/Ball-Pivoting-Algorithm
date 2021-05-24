import unittest
from grid import Grid
from point import Point


class TestGrid(unittest.TestCase):
    def test_create_grid(self):
        points = []

        for i in range(1000):
            p = Point(i, i, i, 0)
            points.append(p)

        grid1 = Grid(radius=1)
        grid1.init_with_data(points)
        self.assertEqual(len(grid1.cells), 500)

        grid2 = Grid(radius=0.5)
        grid2.init_with_data(points)
        self.assertEqual(len(grid2.cells), 1000)

    def test_get_neighbors(self):
        points = []
        center_point = None
        center_point_neighbors = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    p = Point(i+1, j+1, k+1, 0)
                    points.append(p)

                    if i == 1 and j == 1 and k == 1:
                        center_point = p

        grid = Grid(radius=0.5)
        grid.init_with_data(points)

        for point in points:
            neighbor_points = []
            neighbor_cells = point.neighbor_nodes

            for cell in neighbor_cells:
                neighbor_points.extend(grid.get_cell_points(cell))

            self.assertLessEqual(len(neighbor_points), 27)

            if point is center_point:
                center_point_neighbors = neighbor_points

        self.assertLessEqual(len(center_point_neighbors), 27)







