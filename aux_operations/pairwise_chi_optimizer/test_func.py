import unittest

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString

from matplotlib import pyplot
from descartes.patch import PolygonPatch

from pairwise_reopt import compute_pairwise_optimal

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

# Test suite for chi metric function
class pairwiseOptimalTest(unittest.TestCase):
	def setUp(self):
		self.fig = pyplot.figure(1, dpi=90)

	def test_normalCase(self):

		ax = self.fig.add_subplot(121)

		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((0, 0)) 
		initB = Point((2, 1))
		
		plot_2_pols(ax, P1, P2, initA, initB)

		result = compute_pairwise_optimal(P1, P2, initA, initB)
		if result:
			ax = self.fig.add_subplot(122)
			plot_2_pols(ax, result[0], result[1], initA, initB)

		pyplot.show()

	def test_normalCase2(self):
		ax = self.fig.add_subplot(121)

		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((-10, 0)) 
		initB = Point((12, 0))

		plot_2_pols(ax, P1, P2, initA, initB)

		result = compute_pairwise_optimal(P1, P2, initA, initB)
		if result:
			ax = self.fig.add_subplot(122)
			plot_2_pols(ax, result[0], result[1], initA, initB)

		pyplot.show()

	def test_normalCase3(self):
		ax = self.fig.add_subplot(121)

		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((-10, 0)) 
		initB = Point((12, 1))

		plot_2_pols(ax, P1, P2, initA, initB)

		result = compute_pairwise_optimal(P1, P2, initA, initB)
		if result:
			ax = self.fig.add_subplot(122)
			plot_2_pols(ax, result[0], result[1], initA, initB)

		pyplot.show()

	def test_normalCase4(self):
		ax = self.fig.add_subplot(121)

		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((-10, 0)) 
		initB = Point((2, 1))

		plot_2_pols(ax, P1, P2, initA, initB)

		result = compute_pairwise_optimal(P1, P2, initA, initB)
		if result:
			ax = self.fig.add_subplot(122)
			plot_2_pols(ax, result[0], result[1], initA, initB)

		pyplot.show()

	def test_normalCase5(self):
		ax = self.fig.add_subplot(121)

		P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
		P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
		initA = Point((-100, 0)) 
		initB = Point((2, 1))

		plot_2_pols(ax, P1, P2, initA, initB)

		result = compute_pairwise_optimal(P1, P2, initA, initB)
		if result:
			ax = self.fig.add_subplot(122)
			plot_2_pols(ax, result[0], result[1], initA, initB)

		pyplot.show()

	def test_normalCase6(self):
		ax = self.fig.add_subplot(121)

		P1 = Polygon([(0, 0), (0.9, 0), (0.9, 1), (0, 1)], [[(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]])
		P2 = Polygon([(0.9, 0), (1, 0), (1, 1), (0.9, 1)], [])
		initA = Point((0, 0)) 
		initB = Point((1, 1))

		plot_2_pols(ax, P1, P2, initA, initB)

		result = compute_pairwise_optimal(P1, P2, initA, initB)
		if result:
			ax = self.fig.add_subplot(122)
			plot_2_pols(ax, result[0], result[1], initA, initB)

		pyplot.show()		

	def test_normalCase7(self):
		ax = self.fig.add_subplot(121)

		P1 = Polygon([(0, 0), (0.9, 0), (0.9, 1), (0, 1)], [[(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]])
		P2 = Polygon([(0.9, 0), (1, 0), (1, 1), (0.9, 1)], [])
		initA = Point((0, 0)) 
		initB = Point((0, 0))

		plot_2_pols(ax, P1, P2, initA, initB)

		result = compute_pairwise_optimal(P1, P2, initA, initB)
		if result:
			ax = self.fig.add_subplot(122)
			plot_2_pols(ax, result[0], result[1], initA, initB)

		pyplot.show()

	def test_normalCase8(self):
		ax = self.fig.add_subplot(121)

		P1 = Polygon([(0, 0), (1.9, 0), (1.9, 1), (0, 1)], [[(0.2, 0.2), (0.4, 0.2), (0.4, 0.6), (1.6, 0.6), (1.6, 0.2), (1.8, 0.2), (1.8, 0.8), (0.2, 0.8)]])
		P2 = Polygon([(1.9, 0), (2, 0), (2, 1), (1.9, 1)], [])
		initA = Point((0, 0)) 
		initB = Point((1, 0))

		plot_2_pols(ax, P1, P2, initA, initB)

		result = compute_pairwise_optimal(P1, P2, initA, initB)
		if result:
			ax = self.fig.add_subplot(122)
			plot_2_pols(ax, result[0], result[1], initA, initB)

		pyplot.show()

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
