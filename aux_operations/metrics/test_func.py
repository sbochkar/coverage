import unittest

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString

from chi import compute_chi
from chi import compute_num_contours

# Test suite for chi metric function
class computeNumContoursTest(unittest.TestCase):

	def test_computeContours(self):
		P = Polygon([(0,0),(1,0),(1,1),(0,1)])
		r = 0.1
		self.assertEqual(compute_num_contours(P, r), 5)

	def test_computeContours2(self):
		P = Polygon([(0, 0), (1, 0), (1, 0.95), (0, 0.95)])
		r = 0.1
		self.assertEqual(compute_num_contours(P, r), 5)

	def test_computeContours3(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (2, 1), (2, 0), (3, 0), (3, 3), (2, 3), (2, 2), (1, 2), (1, 3), (0, 3)])
		r = 0.1
		self.assertEqual(compute_num_contours(P, r), 9)
		
	def test_computeContourswithHole(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]])
		r = 0.1
		self.assertEqual(compute_num_contours(P, r), 6)

	def test_computeContours4(self):
		P = Polygon([(0, 0), (1, 0), (1, 1.4), (2, 1.4), (2, 0), (3, 0), (3, 3), (2, 3), (2, 1.6), (1, 1.6), (1, 3), (0, 3)])
		r = 0.1
		self.assertEqual(compute_num_contours(P, r), 11)

	def test_computeContours5(self):
		P = Polygon([(0, 0), (1, 0), (1, 1.45), (2, 1.45), (2, 0), (3, 0), (3, 3), (2, 3), (2, 1.55), (1, 1.55), (1, 3), (0, 3)])
		r = 0.1
		self.assertEqual(compute_num_contours(P, r), 11)


# Test suite for chi metric function
class chiTest(unittest.TestCase):

	def test_chiTest(self):
		P = Polygon([(0,0),(1,0),(1,1),(0,1)])
		c = Point((-1, 0))
		
		self.assertEqual(compute_chi(polygon=P, initPos=c, radius=0.1), 1812.0)

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(computeNumContoursTest))
    test_suite.addTest(unittest.makeSuite(chiTest))
    return test_suite

mySuit = suite()
runner = unittest.TextTestRunner()
runner.run(mySuit)
