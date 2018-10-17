import unittest

from shapely.geometry import Polygon
from shapely.geometry import LineString

from polygon_split import polygon_split

# Test suite for polygon split function
class polygonSplitTest(unittest.TestCase):

	def test_polygonSplit_emptyPolygon(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		e = LineString([(0, 0), (1, 1)])
		self.assertEqual(polygon_split([], e), [])

	def test_polygonSplit_emptyEdge(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		e = LineString([(0, 0), (1, 1)])
		self.assertEqual(polygon_split(P, []), [])


	def test_polygonSplit_inccorectEdge2(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		e = LineString([(0, 0), (1, 1), (0, 1)])
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_selfintersectingPolygon(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0.1, -0.1)], [])
		e = LineString([(0, 0), (1, 1)])
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_cutInsidePolygon(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		e = LineString([(0.1, 0.1), (0.9, 0.9)])
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_cutTouchesPolygon(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		e = LineString([(0, 0), (0.9, 0.9)])
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_cutAlongBoundary(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		e = LineString([(0, 0), (0, 1)])
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_nonDecomposingCut(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.2, 0.2),
												(0.2, 0.8),
												(0.8, 0.8),
												(0.8, 0.2)]])
		e = LineString([(0.2, 0), (0.2, 0.2)])
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_cutThroughManyPoints(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.5, 1), (0, 1)], [])
		e = LineString([(0.5, 0), (0.5, 1)])

		R1 = Polygon([(0.5, 0), (0, 0), (0, 1), (0.5, 1), (0.2, 0.8), (0.5, 0.9), (0.5, 0)])
		R2 = Polygon([(0.5, 0.9), (0.8, 1), (1, 1), (1, 0), (0.5, 0), (0.5, 0.9)])

		result1, result2 = polygon_split(P, e)

		self.assertTrue(result1.equals(R1) and result2.equals(R2))

	def test_polygonSplit_cutThroughHole(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.2, 0.2),
												(0.2, 0.8),
												(0.8, 0.8),
												(0.8, 0.2)]])
		e = LineString([(0.2, 0), (0.2, 1)])
		result = polygon_split(P, e)

		R1 = Polygon([(0.2, 0), (0, 0), (0, 1), (0.2, 1), (0.2, 0.8), (0.2, 0.2), (0.2, 0)])
		R2 = Polygon([(0.2, 1), (1, 1), (1, 0), (0.2, 0), (0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8), (0.2, 1)])

		self.assertTrue(R1.equals(result[0]) and R2.equals(result[1]))

	def test_polygonSplit_cutOutsidePolygon1(self):
		P = Polygon([(0, 0), (0.5, 0.5), (1, 0), (1, 1), (0, 1)], [])
		e = LineString([(0, 0), (1, 0)])
		result = polygon_split(P, e)
		self.assertEqual(result, [])

	def test_polygonSplit_validSplit1(self):
	 	P = Polygon([(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.5, 1), (0, 1)],
	 		[[(0.1, 0.1), (0.1, 0.2), (0.2, 0.1)],
	 		 [(0.9, 0.9), (0.9, 0.8), (0.8, 0.8)]])
	 	e = LineString([(0, 0), (0.2, 0.8)])
	 	result = polygon_split(P, e)
	 	self.assertTrue(result)
	 	P1, P2 = result
	 	self.assertTrue(P1)
	 	self.assertTrue(P2)

	 	testPolygon1 = Polygon([(1.0, 0.0), (1.0, 1.0), (0.8, 1.0), (0.2, 0.8), (0.0, 0.0)], [[(0.1, 0.1), (0.1, 0.2), (0.2, 0.1)], [(0.9, 0.9), (0.9, 0.8), (0.8, 0.8)]])
	 	testPolygon2 = Polygon([(0.5, 1.0), (0.0, 1.0), (0.0, 0.0), (0.2, 0.8)])

	 	self.assertTrue(P1.equals(testPolygon1) and P2.equals(testPolygon2))

	def test_polygonSplit_validSplit2(self):
	 	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	 	e = LineString([(0, 0.2), (1, 0.2)])
	 	result = polygon_split(P, e)
	 	self.assertTrue(result)
	 	P1, P2 = result
	 	self.assertTrue(P1)
	 	self.assertTrue(P2)

	 	testPolygon1 = Polygon([(1.0, 0.0), (1.0, 0.2), (0.0, 0.2), (0.0, 0.0)])
	 	testPolygon2 = Polygon([(1.0, 1.0), (0.0, 1.0), (0.0, 0.2), (1.0, 0.2)])

	 	self.assertTrue(P1.equals(testPolygon1) and P2.equals(testPolygon2))

	def test_polygonSplit_validSplit3(self):
		P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		e = LineString([(0.2, 0), (0, 0.2)])
		result = polygon_split(P, e)
		self.assertTrue(result)
		P1, P2 = result
		self.assertTrue(P1)
		self.assertTrue(P2)

	 	testPolygon1 = Polygon([(0.2, 0.0), (0.0, 0.2), (0.0, 0.0)])
	 	testPolygon2 = Polygon([(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.2), (0.2, 0.0)])

	 	self.assertTrue(P1.equals(testPolygon1) and P2.equals(testPolygon2))

	def test_stability(self):
	 	P = Polygon([(0, 0),
	 		  (3, 1),
	 		  (3, 0),
	 		  (4, 1),
	 		  (5, 0),
	 		  (5, 1),
	 		  (7, 1),
	 		  (5, 2),
	 		  (7, 3),
	 		  (0, 4),
	 		  (0, 2.5),
	 		  (1, 2),
	 		  (0, 1.5),
	 		  (1, 1),
	 		  (0, 0.5)], [[(3, 2), (3, 3), (4, 3), (4, 2)]])
		
	 	polyExterior = P.exterior
	
	 	from numpy import linspace
	 	from itertools import product
	 	searchDistances = list(linspace(0, polyExterior.length, 200))

	 	searchSpace = []
	 	for distance in searchDistances:
	 		solutionCandidate = polyExterior.interpolate(distance)
	 		searchSpace.append((solutionCandidate.x, solutionCandidate.y))
	
	 	try:
	 		for cutEdge in product(searchSpace, repeat=2):
	 			cutEdgeLS = LineString(cutEdge)
	 			result = polygon_split(P, cutEdgeLS)
	 	except Exception:
	 		self.fail("Stability test has failed!")


def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(polygonSplitTest))
    return test_suite

mySuit = suite()
runner = unittest.TextTestRunner()
runner.run(mySuit)
