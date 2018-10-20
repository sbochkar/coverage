import unittest

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString

from pairwise_reopt import compute_pairwise_optimal

# Test suite for chi metric function
class pairwiseOptimalTest(unittest.TestCase):

	def test_normalCase(self):
		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((0, 0)) 
		initB = Point((2, 1))
		print(compute_pairwise_optimal(P1, P2, initA, initB))

	def test_normalCase2(self):
		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((-10, 0)) 
		initB = Point((12, 0))
		print(compute_pairwise_optimal(P1, P2, initA, initB))

	def test_normalCase3(self):
		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((-10, 0)) 
		initB = Point((12, 1))
		print(compute_pairwise_optimal(P1, P2, initA, initB))

	def test_normalCase4(self):
		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((-10, 0)) 
		initB = Point((2, 1))
		print(compute_pairwise_optimal(P1, P2, initA, initB))

	def test_normalCase5(self):
		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((-100, 0)) 
		initB = Point((2, 1))
		print(compute_pairwise_optimal(P1, P2, initA, initB))

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(pairwiseOptimalTest))
    return test_suite

mySuit = suite()
runner = unittest.TextTestRunner()
runner.run(mySuit)
