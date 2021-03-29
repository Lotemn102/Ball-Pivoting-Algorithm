import math
from typing import Dict


class Point:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class Node:
    def __init__(self, radius: float, length: float, point: Point, depth: int,
                 parent=None, data=None):
        self.parent = parent
        self.radius = radius
        self.children = {}
        '''
        Boundaries of the structure, (x, y, z) represent front top left corner.

               o ---------- o
              /            /|
             /            / |
            /            /  |
          (x,y,z) ----- o   o
          |             |  /
          |             | /
          |             |/
          o ----------- o

        '''
        self.point = point
        self.length = length
        self.depth = depth
        self.data = data # Only leaves hold data.

    @staticmethod
    def calc_closet_power_of_two(number: float):
        pass

    @property
    def is_leaf(self) -> bool:
        return self.depth == 0

    def insert(self, node, data) -> None:
        if self.is_leaf:
            # Add new node
            pass
        else:
            # Continue traversing the tree.

            # Get the first free index.
            child_index = Octree.calc_first_free_index(self.children)

            # Create new node.

            new_point = Point(node.point+)
            new_node = Node(radius=node.radius, length=node.length / 2, parent=node, point=node.point,
                            depth=node.depth - 1)
            self.children[child_index] = new_node
            self.children[child_index].insert(node, data)


class Octree:
    """
    Create an octree with leaves of size `closet_power_of_two(given_radius)`.
    """
    def __init__(self, radius: float, length: float):
        empty_point = Point(x=0, y=0, z=0)
        depth = math.ceil(math.log2(length / radius))
        self._root = Node(radius=radius, length=length, parent=None, point=empty_point, depth=depth)
        self.radius = radius
        self.edge_length = length

    @staticmethod
    def calc_first_free_index(children: Dict) -> int:
        i = 0

        for i in range(8):
            if i not in children:
                break

        if i is None:
            print("Oh no!")

        return i

    @property
    def root(self):
        return self._root

    @property
    def depth(self) -> float:
        return self.root.depth

    def insert(self, p) -> None:
        point = Point(x=p[0], y=p[1], z=p[2])

        # Convert point to node
        new_node = Node(radius=self.radius, length=self.root.length, data=point, depth=self.root.depth,
                        parent=self.root)

        # Insert.
        self.root.insert(new_node)

















