import math
import numpy as np
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D


class Point:
    def __init__(self, x, y, z):
        self.z = np.float32(z)
        self.y = np.float32(y)
        self.x = np.float32(x)
        self._cell_code = None

    @property
    def cell_code(self):
        return self._cell_code

    @cell_code.setter
    def cell_code(self, code):
        self._cell_code = code


class Grid:
    def __init__(self, radius, points=None):
        self.cells = {}
        self.radius = radius
        self.num_cells = 0
        self.bounding_box_size = 0

        if points is not None:
            self.init_with_data(points)

    @staticmethod
    def _encode_cell(x, y, z):
        # Each coordinate is 8 bytes.
        code = x | (y << 8) | (z << 16)
        return code

    @staticmethod
    def _decode_cell(code):
        mask_x = 0b000000000000000011111111
        x = code & mask_x
        mask_y = 0b000000001111111100000000
        y = (code & mask_y) >> 8
        z = code >> 16
        return int(x), int(y), int(z)

    def show(self):
        """
        Shows only the points currently and not the actual grid.

        :return: None.
        """
        points = [item for sublist in self.cells.values() for item in sublist]

        fig = pyplot.figure()
        ax = Axes3D(fig)
        x_vals = [point.x for point in points]
        y_vals = [point.y for point in points]
        z_vals = [point.z for point in points]

        ax.scatter(x_vals, y_vals, z_vals)
        pyplot.show()

    def init_with_data(self, list_of_points):
        min_x, max_x, min_y, max_y, min_z, max_z = 0, 0, 0, 0, 0, 0

        # Find boundaries for the bounding box of the entire data.
        for point in list_of_points:
            min_x = point.x if point.x < min_x else min_x
            max_x = point.x if point.x > max_x else max_x
            min_y = point.y if point.y < min_y else min_y
            max_y = point.y if point.y > max_y else max_y
            min_z = point.z if point.z < min_z else min_z
            max_z = point.z if point.z > max_z else max_z

        x = max_x - min_x
        y = max_y - min_y
        z = max_z - min_z

        # I'm taking the max since i want the bounding box to be a square.
        self.bounding_box_size = max(x, y, z)

        # Calculate each cell edge size.
        self.num_cells = self.bounding_box_size / (2 * self.radius)

        # Start appending the data points to their cells.
        for point in list_of_points:
            # Find the point's fitting cell. Assuming the bounding box's front-bottom-right corner is the origin (marked
            # with * in the following figure)
            '''
                      y
                      |
                      |________
                     /|        |
                    / |        |
                   /  |        |
                  |   |________|______ x
                  |  /         /
                  | /         /
                  |/________*/
                  /
                 /
                z
            '''

            x_cell = math.floor(point.x / (2 * self.radius))
            y_cell = math.floor(point.y / (2 * self.radius))
            z_cell = math.floor(point.z / (2 * self.radius))

            # Encode cell location.
            code = self._encode_cell(x=x_cell, y=y_cell, z=z_cell)
            point.cell_code = code

            # Add the point to the cell in the hash table.
            if code not in self.cells.keys():
                self.cells[code] = []

            self.cells[code].append(point)

    def get_neighbor_points(self, point):
        neighbor_points = []

        # Find the point's cell.
        x, y, z = self._decode_cell(point.cell_code)

        # Check for each of the possible 8 neighbors if it exists.
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    cell_corner = x + i, y + j, z + k

                    if cell_corner[0] < 0 or cell_corner[1] < 0 or cell_corner[2] < 0:
                        continue

                    cell_code = self._encode_cell(cell_corner[0], cell_corner[1], cell_corner[2])
                    if cell_code in self.cells.keys():
                        neighbor_points.extend(self.cells[cell_code])

        return neighbor_points







