import open3d
import numpy as np

pcd = open3d.geometry.PointCloud()
np_points = np.random.rand(100, 3)

# From numpy to Open3D
pcd.points = open3d.utility.Vector3dVector(np_points)
open3d.visualization.draw_geometries([pcd])

# From Open3D to numpy
#np_points = np.asarray(pcd.points)