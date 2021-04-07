import math
import numpy as np
import cubeshow as cs
from matplotlib import pyplot
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


from edge import Edge
import utils


class Grid:
    def __init__(self, radius, points=None):
        self.all_points = points
        self.cells = {}
        self.radius = radius
        self.num_cells_per_axis = 0
        self.bounding_box_size = 0
        self.edges = []

        if points is not None:
            self.init_with_data(points)

    def show(self):
        """
        Shows only the points currently and not the actual grid.

        Implementation is based on this code:
        https://github.com/safl/ndarray_plot

        :return: None.
        """

        fig = pyplot.figure(dpi=120)
        ax = fig.add_subplot(111, projection='3d')
        ax.axis('off')

        element = {
            "top": np.asarray([[[0, 1], [0, 1]], [[0, 0], [1, 1]], [[1, 1], [1, 1]]]),
            "bottom": np.asarray([[[0, 1], [0, 1]], [[0, 0], [1, 1]], [[0, 0], [0, 0]]]),
            "left": np.asarray([[[0, 0], [0, 0]], [[0, 1], [0, 1]], [[0, 0], [1, 1]]]),
            "right": np.asarray([[[1, 1], [1, 1]], [[0, 1], [0, 1]], [[0, 0], [1, 1]]]),
            "front": np.asarray([[[0, 1], [0, 1]], [[0, 0], [0, 0]], [[0, 0], [1, 1]]]),
            "back": np.asarray([[[0, 1], [0, 1]], [[1, 1], [1, 1]], [[0, 0], [1, 1]]])
        }

        num_cells = math.ceil(self.num_cells_per_axis)
        spacing_factor = 0.05

        for l in range(0, num_cells):
            for m in range(0, num_cells):
                for n in range(0, num_cells):
                    relative_pos = (l * spacing_factor, m * spacing_factor, n * spacing_factor)

                    for side in element:
                        (Ls, Ms, Ns) = (
                            (element[side][0] + l) + relative_pos[0],
                            (element[side][1] + m) + relative_pos[1],
                            (element[side][2] + n) + relative_pos[2]
                        )

                        Ls /= num_cells
                        Ls *= self.bounding_box_size

                        Ms /= num_cells
                        Ms *= self.bounding_box_size

                        Ns /= num_cells
                        Ns *= self.bounding_box_size

                        ax.plot_surface(
                            Ls, Ns, Ms,
                            rstride=1, cstride=1,
                            alpha=0.15,
                            color='gray'
                        )

        points = self.all_points
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
        self.num_cells_per_axis = self.bounding_box_size / (2 * self.radius)

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
            code = utils.encode_cell(x=x_cell, y=y_cell, z=z_cell)
            point.cell_code = code

            # Add the point to the cell in the hash table.
            if code not in self.cells.keys():
                self.cells[code] = []

            self.cells[code].append(point)

    def get_cell_points(self, cell_code):
        points = []

        if cell_code in self.cells.keys():
            p = self.cells[cell_code]
            points.extend(p)

        return points

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def remove_edge(self, edge: Edge):
        self.edges.remove(edge)







