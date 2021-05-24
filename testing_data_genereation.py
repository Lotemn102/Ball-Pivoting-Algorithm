from bpa import BPA
import open3d as o3d
import numpy as np

bpa = BPA(path='output.txt', radius=0.04, visualizer=True)
bpa.visualizer.close()

pcd = o3d.geometry.PointCloud()
points = np.array([(point.x, point.y, point.z) for point in bpa.points])
pcd.points = o3d.utility.Vector3dVector(points)

# Color the point in black.
points_mask = np.zeros(shape=(len(bpa.points), 3))
black_colors = np.zeros_like(points_mask)
pcd.colors = o3d.Vector3dVector(black_colors)

# Set up visualizer.
vis = o3d.visualization.Visualizer()
vis.create_window()
vis.add_geometry(pcd)

points = []

for p in bpa.points:
    # Add the original point
    points.append([p.x, p.y, p.z])

    # Calc another point on that normal vector at fixed distance
    distance = 0.2
    n = np.asarray(p.normal)
    c = (distance / np.sqrt(n[0]*n[0] + n[1]*n[1] + n[2]*n[2])) * n
    c[0] = c[0] + p.x
    c[1] = c[1] + p.y
    c[2] = c[2] + p.z
    points.append(c)

# Add normals lines
normals = []

for i, _ in enumerate(points):
    if i % 10 == 0:
        normals.append([i, i+1])
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