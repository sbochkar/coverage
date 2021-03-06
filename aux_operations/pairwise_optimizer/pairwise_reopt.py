import logging

from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.ops import snap

from numpy import linspace
from itertools import product

from metrics.chi import ChiMetric
from polygon_split.polygon_split import polygon_split


SNAP_TOLLERANCE = 1e-06


# Configure logging properties for this module
logger = logging.getLogger("pairwiseReoptimization")
#fileHandler = logging.FileHandler("logs/pairwiseReoptimization.log")

streamHandler = logging.StreamHandler()

logger.addHandler(streamHandler)
#logger.addHandler(fileHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

streamHandler.setFormatter(formatter)
#fileHandler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)


def compute_pairwise_optimal(polygonA=[],
							 polygonB=[],
							 robotAInitPos=[],
							 robotBInitPos=[],
							 metric=[],
							 nrOfSamples=100,
):
	"""
	Takes two adjacent polygons and attempts to modify the shared edge such that
	the metric chi is reduced.

	TODO:
		Need to investigate assignment of cells to robots.

	Args:
		polygonA: First polygon as Shapely objects.
		polygonB: Second polygon as Shapely objects.
		robotAInitPos: Location of robot A as Shapely Point.
		robotBInitPos: Location of robot B as Shapely Point.
		metric: An instance of metric that will be used to comptue cost of cuts.
		nrOfSamples: Samppling density to be used in the search for optimal cut.

	Returns:
		Returns the cut that minimizes the maximum chi metrix. Or [] if no such
		cut exists or original cut is the best or error has occured.
	
	"""

	# The actual algorithm:
	# 1) Combine the two polygons
	# 2) Find one cut that works better
	# 3) Return that cut or no cut if nothing better was found

	if not polygonA or not polygonB:
		return []

	if not robotAInitPos or not robotBInitPos:
		return []

	if not metric:
		return []

	try:
		snappedPolygon = snap(polygonB, polygonA, SNAP_TOLLERANCE)

		polygonUnion = polygonA.union(snappedPolygon)
	except:
		return []

	# Check if the union is valid and not multigeometry object
	if not isinstance(polygonUnion, Polygon):
		return []
	if not polygonUnion.is_valid or not polygonUnion.is_simple:
		return []

	# Initializae the search space as well original cost
	polyExterior = polygonUnion.exterior

	searchSpace = []
	for distance in linspace(0, polyExterior.length, nrOfSamples):
		solutionCandidate = polyExterior.interpolate(distance)
		searchSpace.append((solutionCandidate.x, solutionCandidate.y))

	# Record the original costs.
	chiL = metric.compute(polygon = polygonA, initialPosition = robotAInitPos)
	chiR = metric.compute(polygon = polygonB, initialPosition = robotBInitPos)

	initMaxChi = max(chiL, chiR)

	minMaxChiFinal = 10e10
	minCandidate = []

	# This search is over any two pairs of samples points on the exterior
	# It is a very costly search.
	for cutEdge in product(searchSpace, repeat=2):

		result = polygon_split(polygonUnion, LineString(cutEdge))

		if result:
			# Resolve cell-robot assignments here.
			# This is to avoid the issue of cell assignments that
			# don't make any sense after polygon cut.
			chiAP1 = metric.compute(polygon = result[0], initialPosition = robotAInitPos)
			chiAP2 = metric.compute(polygon = result[1], initialPosition = robotAInitPos)
			chiBP1 = metric.compute(polygon = result[0], initialPosition = robotBInitPos)
			chiBP2 = metric.compute(polygon = result[1], initialPosition = robotBInitPos)

			maxChiCases = [max(chiAP1, chiBP2),
					  	   max(chiAP2, chiBP1)]

			minMaxChi = min(maxChiCases)
			if minMaxChi <= minMaxChiFinal:
				minCandidate = cutEdge
				minMaxChiFinal = minMaxChi

	logger.debug("Original min max chi as: %4.2f"%initMaxChi)
	logger.debug("Computed min max chi as: %4.2f"%minMaxChiFinal)
	logger.debug("Cut: %s"%(minCandidate, ))

	if initMaxChi <= minMaxChiFinal:
		logger.debug("No cut results in minimum altitude")
		return []

	newPolygons = polygon_split(polygonUnion, LineString(minCandidate))

	# Snap the new polygons to the boundary of old union.
	# This is to preserve the boundary.
	processedPolygon1 = snap(newPolygons[0], polygonUnion, SNAP_TOLLERANCE)
	processedPolygon2 = snap(newPolygons[1], polygonUnion, SNAP_TOLLERANCE)

	return processedPolygon1, processedPolygon2


if __name__ == '__main__':

	chi = ChiMetric(radius=0.1, linearPenalty=1.0, angularPenalty=10*1.0/360)

	P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
	initA = Point((0, 0)) 
	initB = Point((1, 0))
	print(compute_pairwise_optimal(P1, P2, initA, initB, chi))

	P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
	initA = Point((0, 0))
	initB = Point((0, 0))
	print(compute_pairwise_optimal(P1, P2, initA, initB, chi))

	P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
	initA = Point((0, 0))
	initB = Point((0, 1))
	print(compute_pairwise_optimal(P1, P2, initA, initB, chi))