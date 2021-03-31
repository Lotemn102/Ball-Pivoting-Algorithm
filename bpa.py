from grid import Grid, Point


class BPA:
    def __init__(self, path, radius):
        points = self._read_points(path)
        self.grid = Grid(points=points, radius=radius)

    @staticmethod
    def _read_points(path):
        points = []
        f = open(path, "r")
        lines = f.read().splitlines()

        for line in lines:
            coordinates = line.split()

            if len(coordinates) is not 3:
                continue

            p = Point(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]))
            points.append(p)

        return points

    def _find_seed_triangle(self):
        pass

    def create_mesh(self):
        pass

bpa = BPA('bunny.pcd', 0.5)
