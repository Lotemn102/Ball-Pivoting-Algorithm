import open3d as o3d
import numpy as np
from itertools import tee


class Visualizer:
    def __init__(self, points):
        self.points = points
        self.visualizer = None
        self.init_visualiser()
        self.pcd = None
        self.lines_set = None
        self.rotation_angle = 0

    def init_visualiser(self):
        """
        Initialize visualizer.

        :return: None.
        """
        pcd = o3d.geometry.PointCloud()
        points = np.array([(point.x, point.y, point.z) for point in self.points])
        pcd.points = o3d.utility.Vector3dVector(points)

        # Color the point in black.
        points_mask = np.zeros(shape=(len(self.points), 3))
        black_colors = np.zeros_like(points_mask)
        pcd.colors = o3d.Vector3dVector(black_colors)

        # Set up visualizer.
        self.pcd = pcd
        self.visualizer = o3d.visualization.Visualizer()
        self.visualizer.create_window()
        self.visualizer.add_geometry(pcd)

    def update(self, edges, grid_triangles, color='red'):
        """
        Updating only the edges (assuming points don't change).

        :return: None.
        """

        if color == 'red':
            c = [1, 0, 0]
        elif color == 'green':
            c = [0, 1, 0]
        else:
            c = [0, 0, 1]

        lines = [[edge.p1.id, edge.p2.id] for edge in edges]

        for edge in edges:
            if edge.color == []:
                edge.color = c
            if edge.p1.id == 2 and edge.p2.id == 2 or edge.p2.id == 2 and edge.p1.id == 2:
                edge.color = [0, 0, 1]

        colors = [edge.color for edge in edges]
        line_set = o3d.geometry.LineSet()
        points = np.array([(point.x, point.y, point.z) for point in self.points])
        line_set.points = o3d.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)

        facets = []

        for triangle in grid_triangles:
            index_1 = self.points.index(triangle[0])
            index_2 = self.points.index(triangle[1])
            index_3 = self.points.index(triangle[2])
            facets.append([index_1, index_2, index_3])

        facets = np.asarray(facets).astype(np.int32)
        points_triangles = np.array([(point.x, point.y, point.z) for point in self.points])
        mesh = o3d.TriangleMesh()
        mesh.vertices = o3d.Vector3dVector(points_triangles)
        mesh.triangles = o3d.Vector3iVector(facets)

        # Manual fix since i don't define the vertices of a triangle clockwise. If they are anti-clockwise, open3d
        # won't render their mesh.
        mesh.compute_triangle_normals()

        for i, n in enumerate(np.asarray(mesh.triangle_normals)):
            t = mesh.triangles[i]
            p_index = t[0]
            p = self.points[p_index]
            if np.dot(n, p.normal) < 0:
                mesh.triangles[i] = np.flip(t)

        self.visualizer.get_render_option().point_size = 3.5
        self.visualizer.add_geometry(line_set)
        self.visualizer.add_geometry(mesh)

        # Rotate the object.
        ctr = self.visualizer.get_view_control()
        self.rotation_angle += 4
        ctr.rotate(x=self.rotation_angle, y=0)

        self.visualizer.update_geometry()
        self.visualizer.poll_events()
        self.visualizer.update_renderer()

    def lock(self):
        """
        Lock the visualizer. Program will stop until user closes the visualizer's window.

        :return: None.
        """
        self.visualizer.run()

    def close(self):
        """
        Close visualizer's window.

        :return: None.
        """
        self.visualizer.close()

    def draw_with_normals(self, percentage=10, normals_size=1):
        """
        Draw the point cloud with it's normals.

        :param percentage: What percentage of normals to draw. Integer number in range [1, 100].
        :return: None.
        """
        self.visualizer.close()

        pcd = o3d.geometry.PointCloud()
        points = np.array([(point.x, point.y, point.z) for point in self.points])
        pcd.points = o3d.utility.Vector3dVector(points)

        # Color the point in black.
        points_mask = np.zeros(shape=(len(self.points), 3))
        black_colors = np.zeros_like(points_mask)
        pcd.colors = o3d.Vector3dVector(black_colors)

        # Set up visualizer.
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(pcd)

        points = []

        for p in self.points:
            # Add the original point
            points.append([p.x, p.y, p.z])

            # Calc another point on that normal vector at fixed distance
            distance = normals_size
            n = np.asarray(p.normal)
            c = (distance / np.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2])) * n
            c[0] = c[0] + p.x
            c[1] = c[1] + p.y
            c[2] = c[2] + p.z
            points.append(c)

        # Add normals lines
        normals = []

        for i, _ in enumerate(points):
            if i % (100 / percentage) == 0:
                normals.append([i, i + 1])
            else:
                normals.append([0, 0])

        colors = [[1, 0, 0] for _ in points]

        line_set = o3d.geometry.LineSet()
        points = np.array([(point[0], point[1], point[2]) for point in points])
        line_set.points = o3d.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(normals)
        line_set.colors = o3d.utility.Vector3dVector(colors)
        vis.add_geometry(line_set)
        vis.update_geometry()
        vis.poll_events()
        vis.update_renderer()
        vis.run()