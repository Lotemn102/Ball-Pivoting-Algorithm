import math
import numpy as np


def calc_distance_points(p1, p2) -> float:
    """
    Calculate the distance between 2 3D points.

    :param p1: First point.
    :param p2: Second point.
    :return: Distance between the points.
    """
    return math.sqrt(math.pow((p2.x - p1.x), 2) + math.pow((p2.y - p1.y), 2) + math.pow((p2.z - p1.z), 2))


def calc_distance_point_to_edge(point, edge) -> float:
    """
    Calculate the distance of a point to an edge. Taken from here: https://math.stackexchange.com/q/1905581

    :param point: The point.
    :param edge: The edge.
    :return: The distance.
    """
    v1 = [edge.p1.x - point.x, edge.p1.y - point.y, edge.p1.z - point.z]
    v2 = [edge.p1.x - edge.p2.x, edge.p1.y - edge.p2.y, edge.p1.z - edge.p2.z]
    return np.linalg.norm(np.cross(v1, v2)) / np.linalg.norm(v2)


def calc_incircle_radius(p1, p2, p3) -> float:
    """
    Calculate the radius of the incircle in a triangle.
    Based on this formula:
     https://en.wikipedia.org/wiki/Incircle_and_excircles_of_a_triangle#Radius

    :param p1: First point of triangle.
    :param p2: Second point of triangle.
    :param p3: Third point of triangle.
    :return: The radius of the incircle.
    """

    edge_1_length = calc_distance_points(p1, p2)
    edge_2_length = calc_distance_points(p2, p3)
    edge_3_length = calc_distance_points(p1, p3)

    s = (edge_1_length + edge_2_length + edge_3_length) / 2
    r = math.sqrt(((s - edge_1_length)*(s - edge_2_length)*(s - edge_3_length)) / s)
    return r


def calc_min_max_angle_of_triangle(e1, e2, e3) -> (float, float):
    """
    Calculate the minimum and maximum angles of a triangle.

    :param e1: First edge.
    :param e2: Second edge.
    :param e3: Third edge.
    :return: minimum angel, maximum angel.
    """
    v1 = [e1.p1.x - e1.p2.x, e1.p1.y - e1.p2.y, e1.p1.z - e1.p2.z]
    v2 = [e2.p1.x - e2.p2.x, e2.p1.y - e2.p2.y, e2.p1.z - e2.p2.z]
    v3 = [e3.p1.x - e3.p2.x, e3.p1.y - e3.p2.y, e3.p1.z - e3.p2.z]

    angle1 = np.arccos((np.dot(v1, v2))/(np.linalg.norm(v1) * np.linalg.norm(v2))) * (180 / np.pi)
    angle2 = np.arccos((np.dot(v1, v3))/(np.linalg.norm(v1) * np.linalg.norm(v3))) * (180 / np.pi)
    angle3 = np.arccos((np.dot(v2, v3))/(np.linalg.norm(v2) * np.linalg.norm(v3))) * (180 / np.pi)

    return min(angle1, angle2, angle3), max(angle1, angle2, angle3)


def encode_cell(x, y, z):
    """
    Encode 3 numbers into a single one.

    :param x: First number.
    :param y: Second number.
    :param z: Third number.
    :return: Code.
    """
    # Assuming each coordinate is 8 bytes.
    code = x | (y << 8) | (z << 16)
    return code


def decode_cell(code):
    """
    Decode a unique number into 3 number.

    :param code: The code
    :return: 3 numbers.
    """
    mask_x = 0b000000000000000011111111
    x = code & mask_x
    mask_y = 0b000000001111111100000000
    y = (code & mask_y) >> 8
    z = code >> 16
    return int(x), int(y), int(z)

