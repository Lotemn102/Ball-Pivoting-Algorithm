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
        self.triangles = []
        self.cell_size = 0

        if points is not None:
            self.init_with_data(points)

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
        self.cell_size = self.bounding_box_size / self.num_cells_per_axis

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

            x_cell = int((point.x // self.cell_size) * self.cell_size)
            y_cell = int((point.y // self.cell_size) * self.cell_size)
            z_cell = int((point.z // self.cell_size) * self.cell_size)

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
