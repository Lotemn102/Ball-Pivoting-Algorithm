import math


def calc_distance(p1, p2):
    """
    Calculate the distance between 2 3D points.

    :param p1: First point.
    :param p2: Second point.
    :return: Distance between the points.
    """
    return math.sqrt(math.pow((p2.x - p1.x), 2) + math.pow((p2.y - p1.y), 2) + math.pow((p2.z - p1.z), 2))


def calc_incircle_radius(p1, p2, p3):
    """
    Calculate the radius of the incircle in a triangle.
    Based on this formula:
     https://en.wikipedia.org/wiki/Incircle_and_excircles_of_a_triangle#Radius

    :param p1: First point of triangle.
    :param p2: Second point of triangle.
    :param p3: Third point of triangle.
    :return: The radius of the incircle.
    """

    edge_1_length = calc_distance(p1, p2)
    edge_2_length = calc_distance(p2, p3)
    edge_3_length = calc_distance(p1, p3)

    s = (edge_1_length + edge_2_length + edge_3_length) / 2
    r = math.sqrt(((s - edge_1_length)*(s - edge_2_length)*(s - edge_3_length)) / s)
    return r


def encode_cell(x, y, z):
    # Assuming each coordinate is 8 bytes.
    code = x | (y << 8) | (z << 16)
    return code


def decode_cell(code):
    mask_x = 0b000000000000000011111111
    x = code & mask_x
    mask_y = 0b000000001111111100000000
    y = (code & mask_y) >> 8
    z = code >> 16
    return int(x), int(y), int(z)

