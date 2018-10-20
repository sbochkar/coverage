import logging

from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString

from numpy import linspace
from itertools import product

from metrics.chi import compute_chi
from polygon_split.polygon_split import polygon_split


RADIUS = 0.1
LINEAR_PENALTY = 1		# Weights for the cost function
ANGULAR_PENALTY = 10	# Weights for the cost function


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


def poly_shapely_to_canonical(polygon=[]):
	"""
	A simple helper function to convert a shapely object representing a polygon
	intop a cononical form polygon.

	Args:
		polygon: A shapely object representing a polygon

	Returns:
		A polygon in canonical form.
	"""

	if not polygon:
		return []

	canonicalPolygon = []
	
	if polygon.exterior.is_ccw:
		polyExterior = list(polygon.exterior.coords)
	else:
		polyExterior = list(polygon.exterior.coords)[::-1]


	holes = []
	for hole in polygon.interiors:
		if hole.is_ccw:
			holes.append(list(polygon.exterior.coords)[::-1])
		else:
			holes.append(list(polygon.exterior.coords))

	canonicalPolygon.append(polyExterior)
	canonicalPolygon.append(holes)

	return canonicalPolygon


def compute_pairwise_optimal(polygonA=[],
							 polygonB=[],
							 robotAInitPos=[],
							 robotBInitPos=[],
							 nrOfSamples=100,
							 radius = 0.1,
							 linPenalty = 1.0,
							 angPenalty = 10*1.0/360):
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
		nrOfSamples: Samppling density to be used in the search for optimal cut.
		raduis: Radius of the coverage implement.
		linPenalty: Linear penalty for computing chi metric.
		angPenalty: Angular penalty for computing chi metric.

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

	try:
		polygonUnion = polygonA.union(polygonB)
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
	chiL = compute_chi(polygon = polygonA,
						initPos = robotAInitPos,
						radius = radius,
						linPenalty = linPenalty,
						angPenalty = angPenalty)
	chiR = compute_chi(polygon = polygonB,
						initPos = robotBInitPos,
						radius = radius,
						linPenalty = linPenalty,
						angPenalty = angPenalty)

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
			chiAP1 = compute_chi(polygon = result[0],
							   	initPos = robotAInitPos,
							   	radius = radius,
							   	linPenalty = linPenalty,
							   	angPenalty = angPenalty)
			chiAP2 = compute_chi(polygon = result[1],
							   	initPos = robotAInitPos,
							   	radius = radius,
							   	linPenalty = linPenalty,
							   	angPenalty = angPenalty)
			chiBP1 = compute_chi(polygon = result[0],
							   	initPos = robotBInitPos,
							   	radius = radius,
							   	linPenalty = linPenalty,
							   	angPenalty = angPenalty)							   	
			chiBP2 = compute_chi(polygon = result[1],
							   	initPos = robotBInitPos,
							   	radius = radius,
							   	linPenalty = linPenalty,
							   	angPenalty = angPenalty)

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
	return newPolygons


if __name__ == '__main__':

	P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
	initA = Point((0, 0)) 
	initB = Point((1, 0))
	print(compute_pairwise_optimal(P1, P2, initA, initB))

	P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
	initA = Point((0, 0))
	initB = Point((0, 0))
	print(compute_pairwise_optimal(P1, P2, initA, initB))

	P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
	initA = Point((0, 0))
	initB = Point((0, 1))
	print(compute_pairwise_optimal(P1, P2, initA, initB))
