import unittest

from grid import Grid
from point import Point
from bpa import BPA


class TestBPA(unittest.TestCase):
    '''
    def test_create_test_file(self):
        f = open("test_1_no_normal.txt", "w")

        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    point_as_string = str(i + 1) + " " + str(j + 1) + " " + str(k + 1) + "\n"
                    f.write(point_as_string)

        f.close()
    '''

    def test_find_seed(self):
        # TODO: This doesn't work properly
        bpa = BPA(path='test_1_no_normal.txt', radius=0.5)
        bpa.find_seed_triangle()




