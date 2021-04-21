import open3d as o3d
import numpy as np
from bpa import BPA
import time

bpa = BPA(path='tests/bunny_with_normals.txt', radius=0.002)

if __name__ == "__main__":
    pcd = o3d.geometry.PointCloud()
    # Color the point in black.
    points_mask = np.zeros(shape=(len(bpa.points), 3))
    black_colors = np.zeros_like(points_mask)
    pcd.colors = o3d.Vector3dVector(black_colors)
    tuple_points = [(point.x, point.y, point.z) for point in bpa.points]
    np_points = np.array(tuple_points)
    pcd.points = o3d.utility.Vector3dVector(np_points)

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(pcd)

    for i in range(100):
        bpa.find_seed_triangle()

        lines = [[edge.p1.id, edge.p2.id] for edge in bpa.grid.edges]
        colors = [[1, 0, 0] for _ in range(len(lines))]
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.Vector3dVector(np_points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)

        vis.add_geometry(line_set)
        vis.update_geometry()
        vis.poll_events()
        vis.update_renderer()

    vis.run()
    vis.destroy_window()




    #vis.update_geometry()
    #vis.update_renderer()
    #vis.poll_events()
    #vis.run()




