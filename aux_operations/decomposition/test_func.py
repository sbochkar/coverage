import unittest

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString

from matplotlib import pyplot
from descartes.patch import PolygonPatch

from decomposition import Decomposition
from metrics.chi import ChiMetric

def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, 'o', color='#999999', zorder=1)

def plot_2_pols(ax, P1, P2, initA, initB):
	patch1 = PolygonPatch(P1, facecolor='blue', edgecolor='#6699cc', alpha=0.5, zorder=2)
	patch2 = PolygonPatch(P2, facecolor='red', edgecolor='#6699cc', alpha=0.5, zorder=2)
	plot_coords(ax, initA.coords)
	plot_coords(ax, initB.coords)

	ax.add_patch(patch1)
	ax.add_patch(patch2)

	ax.set_title('Original')

	minx1, miny1, maxx1, maxy1 = P1.bounds
	minx2, miny2, maxx2, maxy2 = P2.bounds
	minx = min(int(minx1)-1, int(minx2)-1, int(initA.x), int(initB.x))
	miny = min(int(miny1)-1, int(miny2)-1, int(initA.y), int(initB.y))
	maxx = max(int(maxx1)+1, int(maxx2)+1, int(initA.x), int(initB.x))
	maxy = max(int(maxy1)+1, int(maxy2)+1, int(initA.y), int(initB.y))

	xrange = [minx, maxx]
	yrange = [miny, maxy]
	ax.set_xlim(*xrange)
	ax.set_xticks(range(*xrange) + [xrange[-1]])
	ax.set_ylim(*yrange)
	ax.set_yticks(range(*yrange) + [yrange[-1]])
	ax.set_aspect(1)

# Test suite for global optimizer
class decompositionTest(unittest.TestCase):
    def setUp(self):
        self.fig = pyplot.figure(1, dpi=90)
        self.chi = ChiMetric(radius=0.1, linearPenalty=1.0, angularPenalty=10*1.0/360)

    def test_createDecomp(self):
        decomp = Decomposition(self.chi)

    def test_addOnePolygon(self):
        decomp = Decomposition(self.chi)

        polygon = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition = Point((0,0))
        polyId = decomp.add_polygon(polygon=polygon, robotPosition=robotPosition)

        self.assertEqual(len(decomp.id2Polygon.keys()), 1)
        self.assertEqual(decomp.id2Polygon.keys()[0], polyId)
        self.assertEqual(decomp.id2Polygon[polyId], polygon)
        
        self.assertEqual(decomp.id2Position[polyId], robotPosition)
        
        self.assertEqual(decomp.id2Cost[polyId], self.chi.compute(polygon=polygon, initialPosition=robotPosition))
        
        self.assertEqual(decomp.id2Adjacent[polyId], [])
        self.assertEqual(len(decomp.id2Adjacent.keys()), 1)

        self.assertEqual(len(decomp.sortedCosts), 1)
        self.assertEqual(decomp.sortedCosts[0], polyId)

    def test_addOneInvalidPolygon(self):
        decomp = Decomposition(self.chi)

        polygon = Polygon([(0,0),(1,0),(1,-1),(1,1),(0,1)])
        robotPosition = Point((0,0))
        polyId = decomp.add_polygon(polygon=polygon, robotPosition=robotPosition)

        self.assertLess(polyId, 0)

        self.assertEqual(len(decomp.id2Polygon.keys()), 0)
        
        self.assertEqual(len(decomp.id2Position), 0)
        
        self.assertEqual(len(decomp.id2Cost), 0)
        
        self.assertEqual(len(decomp.id2Adjacent), 0)

        self.assertEqual(len(decomp.sortedCosts), 0)

    def test_addTwoPolygon(self):
        decomp = Decomposition(self.chi)

        polygon1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition1 = Point((0,0))
        polyId1 = decomp.add_polygon(polygon=polygon1, robotPosition=robotPosition1)

        polygon2 = Polygon([(1,0),(2,0),(2,1),(1,1)])
        robotPosition2 = Point((1,0))
        polyId2 = decomp.add_polygon(polygon=polygon2, robotPosition=robotPosition2)

        self.assertEqual(len(decomp.id2Polygon.keys()), 2)
        self.assertEqual(decomp.id2Polygon[polyId1], polygon1)
        self.assertEqual(decomp.id2Polygon[polyId2], polygon2)
        
        self.assertEqual(decomp.id2Position[polyId1], robotPosition1)
        self.assertEqual(decomp.id2Position[polyId2], robotPosition2)
        
        self.assertEqual(decomp.id2Cost[polyId1], self.chi.compute(polygon=polygon1, initialPosition=robotPosition1))
        self.assertEqual(decomp.id2Cost[polyId2], self.chi.compute(polygon=polygon2, initialPosition=robotPosition2))
        
        self.assertEqual(len(decomp.id2Adjacent.keys()), 2)
        self.assertEqual(decomp.id2Adjacent[polyId1], [polyId2])
        self.assertEqual(decomp.id2Adjacent[polyId2], [polyId1])

        self.assertEqual(len(decomp.sortedCosts), 2)
        self.assertEqual(decomp.sortedCosts[0], polyId1)
        self.assertEqual(decomp.sortedCosts[1], polyId2)

    def test_addTwoFarPolygon(self):
        decomp = Decomposition(self.chi)

        polygon1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition1 = Point((0,0))
        polyId1 = decomp.add_polygon(polygon=polygon1, robotPosition=robotPosition1)

        polygon2 = Polygon([(2,0),(3,0),(3,1),(2,1)])
        robotPosition2 = Point((2,0))
        polyId2 = decomp.add_polygon(polygon=polygon2, robotPosition=robotPosition2)

        self.assertEqual(len(decomp.id2Polygon.keys()), 2)
        self.assertEqual(decomp.id2Polygon[polyId1], polygon1)
        self.assertEqual(decomp.id2Polygon[polyId2], polygon2)
        
        self.assertEqual(decomp.id2Position[polyId1], robotPosition1)
        self.assertEqual(decomp.id2Position[polyId2], robotPosition2)
        
        self.assertEqual(decomp.id2Cost[polyId1], self.chi.compute(polygon=polygon1, initialPosition=robotPosition1))
        self.assertEqual(decomp.id2Cost[polyId2], self.chi.compute(polygon=polygon2, initialPosition=robotPosition2))
        
        self.assertEqual(len(decomp.id2Adjacent.keys()), 2)
        self.assertEqual(decomp.id2Adjacent[polyId1], [])
        self.assertEqual(decomp.id2Adjacent[polyId2], [])

        self.assertEqual(len(decomp.sortedCosts), 2)
        self.assertEqual(decomp.sortedCosts[0], polyId1)
        self.assertEqual(decomp.sortedCosts[1], polyId2)

    def test_addTwoOverlappingPolygon(self):
        decomp = Decomposition(self.chi)

        polygon1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition1 = Point((0,0))
        polyId1 = decomp.add_polygon(polygon=polygon1, robotPosition=robotPosition1)

        polygon2 = Polygon([(0.5,0),(1.5,0),(1.5,1),(0.5,1)])
        robotPosition2 = Point((0.5,0))
        polyId2 = decomp.add_polygon(polygon=polygon2, robotPosition=robotPosition2)

        self.assertEqual(len(decomp.id2Polygon.keys()), 2)
        self.assertEqual(decomp.id2Polygon[polyId1], polygon1)
        self.assertEqual(decomp.id2Polygon[polyId2], polygon2)
        
        self.assertEqual(decomp.id2Position[polyId1], robotPosition1)
        self.assertEqual(decomp.id2Position[polyId2], robotPosition2)
        
        self.assertEqual(decomp.id2Cost[polyId1], self.chi.compute(polygon=polygon1, initialPosition=robotPosition1))
        self.assertEqual(decomp.id2Cost[polyId2], self.chi.compute(polygon=polygon2, initialPosition=robotPosition2))
        
        self.assertEqual(len(decomp.id2Adjacent.keys()), 2)
        self.assertEqual(decomp.id2Adjacent[polyId1], [polyId2])
        self.assertEqual(decomp.id2Adjacent[polyId2], [polyId1])

        self.assertEqual(len(decomp.sortedCosts), 2)
        self.assertEqual(decomp.sortedCosts[0], polyId1)
        self.assertEqual(decomp.sortedCosts[1], polyId2)

    def test_addTwoTouchingPolygon(self):
        decomp = Decomposition(self.chi)

        polygon1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition1 = Point((0,0))
        polyId1 = decomp.add_polygon(polygon=polygon1, robotPosition=robotPosition1)

        polygon2 = Polygon([(1,1),(2,1),(2,2),(1,2)])
        robotPosition2 = Point((1,1))
        polyId2 = decomp.add_polygon(polygon=polygon2, robotPosition=robotPosition2)

        self.assertEqual(len(decomp.id2Polygon.keys()), 2)
        self.assertEqual(decomp.id2Polygon[polyId1], polygon1)
        self.assertEqual(decomp.id2Polygon[polyId2], polygon2)
        
        self.assertEqual(decomp.id2Position[polyId1], robotPosition1)
        self.assertEqual(decomp.id2Position[polyId2], robotPosition2)
        
        self.assertEqual(decomp.id2Cost[polyId1], self.chi.compute(polygon=polygon1, initialPosition=robotPosition1))
        self.assertEqual(decomp.id2Cost[polyId2], self.chi.compute(polygon=polygon2, initialPosition=robotPosition2))
        
        self.assertEqual(len(decomp.id2Adjacent.keys()), 2)
        self.assertEqual(decomp.id2Adjacent[polyId1], [])
        self.assertEqual(decomp.id2Adjacent[polyId2], [])

        self.assertEqual(len(decomp.sortedCosts), 2)
        self.assertEqual(decomp.sortedCosts[0], polyId1)
        self.assertEqual(decomp.sortedCosts[1], polyId2)

    def test_addThreePolygons(self):
        decomp = Decomposition(self.chi)

        polygon1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition1 = Point((0,0))
        polyId1 = decomp.add_polygon(polygon=polygon1, robotPosition=robotPosition1)

        polygon2 = Polygon([(2,0),(3,0),(3,1),(2,1)])
        robotPosition2 = Point((20,0))
        polyId2 = decomp.add_polygon(polygon=polygon2, robotPosition=robotPosition2)

        polygon3 = Polygon([(1,0),(2,0),(2,1),(1,1)])
        robotPosition3 = Point((1,0))
        polyId3 = decomp.add_polygon(polygon=polygon3, robotPosition=robotPosition3)        

        self.assertEqual(len(decomp.id2Polygon.keys()), 3)
        self.assertEqual(decomp.id2Polygon[polyId1], polygon1)
        self.assertEqual(decomp.id2Polygon[polyId2], polygon2)
        self.assertEqual(decomp.id2Polygon[polyId3], polygon3)
        
        self.assertEqual(decomp.id2Position[polyId1], robotPosition1)
        self.assertEqual(decomp.id2Position[polyId2], robotPosition2)
        self.assertEqual(decomp.id2Position[polyId3], robotPosition3)
        
        self.assertEqual(decomp.id2Cost[polyId1], self.chi.compute(polygon=polygon1, initialPosition=robotPosition1))
        self.assertEqual(decomp.id2Cost[polyId2], self.chi.compute(polygon=polygon2, initialPosition=robotPosition2))
        self.assertEqual(decomp.id2Cost[polyId3], self.chi.compute(polygon=polygon3, initialPosition=robotPosition3))
        
        self.assertEqual(len(decomp.id2Adjacent.keys()), 3)
        self.assertEqual(decomp.id2Adjacent[polyId1], [polyId3])
        self.assertEqual(decomp.id2Adjacent[polyId2], [polyId3])
        self.assertEqual(decomp.id2Adjacent[polyId3], [polyId1, polyId2])

        self.assertEqual(len(decomp.sortedCosts), 3)
        self.assertEqual(decomp.sortedCosts[0], polyId1)
        self.assertEqual(decomp.sortedCosts[1], polyId3)
        self.assertEqual(decomp.sortedCosts[2], polyId2)

    def test_removeFromThree(self):
        decomp = Decomposition(self.chi)

        polygon1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition1 = Point((0,0))
        polyId1 = decomp.add_polygon(polygon=polygon1, robotPosition=robotPosition1)

        polygon2 = Polygon([(2,0),(3,0),(3,1),(2,1)])
        robotPosition2 = Point((20,0))
        polyId2 = decomp.add_polygon(polygon=polygon2, robotPosition=robotPosition2)

        polygon3 = Polygon([(1,0),(2,0),(2,1),(1,1)])
        robotPosition3 = Point((1,0))
        polyId3 = decomp.add_polygon(polygon=polygon3, robotPosition=robotPosition3)        

        self.assertTrue(decomp.remove_polygon(polyId3))

        self.assertEqual(len(decomp.id2Polygon.keys()), 2)
        self.assertEqual(decomp.id2Polygon[polyId1], polygon1)
        self.assertEqual(decomp.id2Polygon[polyId2], polygon2)
        
        self.assertEqual(decomp.id2Position[polyId1], robotPosition1)
        self.assertEqual(decomp.id2Position[polyId2], robotPosition2)
        
        self.assertEqual(decomp.id2Cost[polyId1], self.chi.compute(polygon=polygon1, initialPosition=robotPosition1))
        self.assertEqual(decomp.id2Cost[polyId2], self.chi.compute(polygon=polygon2, initialPosition=robotPosition2))
        
        self.assertEqual(len(decomp.id2Adjacent.keys()), 2)
        self.assertEqual(decomp.id2Adjacent[polyId1], [])
        self.assertEqual(decomp.id2Adjacent[polyId2], [])

        self.assertEqual(len(decomp.sortedCosts), 2)
        self.assertEqual(decomp.sortedCosts[0], polyId1)
        self.assertEqual(decomp.sortedCosts[1], polyId2)

    def test_addAfterRemove(self):
        decomp = Decomposition(self.chi)

        polygon1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition1 = Point((0,0))
        polyId1 = decomp.add_polygon(polygon=polygon1, robotPosition=robotPosition1)

        polygon2 = Polygon([(2,0),(3,0),(3,1),(2,1)])
        robotPosition2 = Point((20,0))
        polyId2 = decomp.add_polygon(polygon=polygon2, robotPosition=robotPosition2)

        polygon3 = Polygon([(1,0),(2,0),(2,1),(1,1)])
        robotPosition3 = Point((1,0))
        polyId3 = decomp.add_polygon(polygon=polygon3, robotPosition=robotPosition3)

        decomp.remove_polygon(polyId1)

        polygon1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
        robotPosition1 = Point((0,0))
        polyId1 = decomp.add_polygon(polygon=polygon1, robotPosition=robotPosition1)

        self.assertEqual(len(decomp.id2Polygon.keys()), 3)
        self.assertEqual(decomp.id2Polygon[polyId1], polygon1)
        self.assertEqual(decomp.id2Polygon[polyId2], polygon2)
        
def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(decompositionTest))
    return test_suite

mySuit = suite()
runner = unittest.TextTestRunner()
runner.run(mySuit)
