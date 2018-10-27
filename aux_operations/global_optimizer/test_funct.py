import unittest

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString

from matplotlib import pyplot
from descartes.patch import PolygonPatch

from decomposition.decomposition import Decomposition
from global_optimizer import global_optimize
from recursive_step import dft_recursion
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
class globalOptimizerTest(unittest.TestCase):
    def setUp(self):
        self.fig = pyplot.figure(1, dpi=90)
        self.chi = ChiMetric(radius=0.1, linearPenalty=1.0, angularPenalty=10*1.0/360)

    def test_normalCase(self):
        ax = self.fig.add_subplot(121)

        decomp = Decomposition(self.chi)

        polyId1 = decomp.add_polygon(polygon=Polygon([(0.0,0.0),(10.0,0.0), (10.0,0.5)],[]), robotPosition=Point((0.0,0.0)))
        polyId2 = decomp.add_polygon(polygon=Polygon([(0.0,0.0),(10.0,0.5),(10.0,1.0),(5.0,0.5)],[]), robotPosition=Point((10.0,0.0)))
        polyId3 = decomp.add_polygon(polygon=Polygon([(5.0,0.5),(10.0,1.0),(0.0,1.0)],[]), robotPosition=Point((10.0,1.0)))
        polyId4 = decomp.add_polygon(polygon=Polygon([(0.0,0.0),(5.0,0.5),(0.0,1.0)],[]), robotPosition=Point((0.0,1.0)))
             
        global_optimize(decomposition=decomp, metric=self.chi)

# Test suite for global optimizer
class recursiveStepTest(unittest.TestCase):
    def setUp(self):
        self.fig = pyplot.figure(1, dpi=90)
        self.chi = ChiMetric(radius=0.1, linearPenalty=1.0, angularPenalty=10*1.0/360)

    def test_normalCase(self):
        ax = self.fig.add_subplot(121)

        decomp = Decomposition(self.chi)

        polyId1 = decomp.add_polygon(polygon=Polygon([(0.0,0.0),(2.5,0.0),(2.5,1.0),(0.0,1.0)],[]), robotPosition=Point((10,0)))
        polyId2 = decomp.add_polygon(polygon=Polygon([(2.5,0.0),(5.0,0.0),(5.0,1.0),(2.5,1.0)],[]), robotPosition=Point((10,1)))
        polyId3 = decomp.add_polygon(polygon=Polygon([(5.0,0.0),(7.5,0.0),(7.5,1.0),(5.0,1.0)],[]), robotPosition=Point((0,1)))
        polyId4 = decomp.add_polygon(polygon=Polygon([(7.5,0.0),(10.0,0.0),(10.0,1.0),(7.5,1.0)],[]), robotPosition=Point((0,0)))

        dft_recursion(decomp, 3, self.chi)


def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(globalOptimizerTest))
    test_suite.addTest(unittest.makeSuite(recursiveStepTest))
    return test_suite

mySuit = suite()
runner = unittest.TextTestRunner()
runner.run(mySuit)
