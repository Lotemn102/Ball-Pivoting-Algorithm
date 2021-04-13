import math
import numpy as np
import open3d

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
        Shows the grid with the points and edges.

        Implementation is based on this code:
        https://github.com/safl/ndarray_plot

        :return: None.
        """
        pcd = open3d.geometry.PointCloud()
        # Color the point in black.
        points_mask = np.zeros(shape=(len(self.all_points), 3))
        black_colors = np.zeros_like(points_mask)
        pcd.colors = open3d.Vector3dVector(black_colors)
        tuple_points = [(point.x, point.y, point.z) for point in self.all_points]
        np_points = np.array(tuple_points)

        # From numpy to Open3D
        pcd.points = open3d.utility.Vector3dVector(np_points)
        open3d.visualization.draw_geometries([pcd])


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







