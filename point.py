import numpy as np
import utils
from typing import List

class Point:
    def __init__(self, x, y, z, id, normal=None):
        self.z = np.float32(z)
        self.y = np.float32(y)
        self.x = np.float32(x)
        self.cell_code = None
        self.normal = normal
        self.id = id
        self.is_used = False

    def __lt__(self, other):
        return self.z <= other.z

    @property
    def neighbor_nodes(self) -> List:
        """
        Get all the points neighbor points.

        :return: List of neighbor points.
        """
        neighbor_nodes = [self.cell_code]

        # Find the point's cell.
        x, y, z = utils.decode_cell(self.cell_code)

        # Check for each of the possible 8 neighbors if it exists.
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    cell_corner = x + i, y + j, z + k

                    if cell_corner[0] < 0 or cell_corner[1] < 0 or cell_corner[2] < 0:
                        continue

                    cell_code = utils.encode_cell(cell_corner[0], cell_corner[1], cell_corner[2])
                    neighbor_nodes.append(cell_code)

        return neighbor_nodes




