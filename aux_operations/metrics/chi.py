import logging
from math import sqrt

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon


# Configure logging properties for this module
logger = logging.getLogger("chi")
#fileHandler = logging.FileHandler("logs/chi.log")

streamHandler = logging.StreamHandler()

#logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)


def compute_num_contours(polygon=[], radius=1):
	"""
	Computing contours of P.

	Params:
		polygon: A shapely object representing the polygon
		radius: Radius of the coverage implement.
	Returns:
		Number of contours
	"""

	numContours = 0

	offsetDist = -0.5*radius

	# TODO: Analyze the effects of join_styles
	testPolygon = Polygon(polygon).buffer(offsetDist)
	while not testPolygon.is_empty:

		if isinstance(testPolygon, Polygon):
			numHoles = len(testPolygon.interiors)
			numContours += 1 + numHoles
			print("Single collection contours: %s"%numContours)

		elif isinstance(testPolygon, MultiPolygon):
			numHoles = 0

			for poly in testPolygon:
				numHoles += len(poly.interiors)
			numContours += len(testPolygon) + numHoles
			print("Multi collection contours: %s"%numContours)
			print(testPolygon)
		
		testPolygon = testPolygon.buffer(-radius)

	logger.debug("Number of contours: %d"%numContours)

	return numContours


def compute_chi(polygon=[], initPos=[], radius=1, linPenalty=1.0, angPenalty=1.0):
	"""
	Metric chi: Approximation of the cost of a coverage path for a polygon

	F1: distance from robot to the polygon and back
	F2: sum of lengths of straight line segments
	F3: approximation of the angular component of polygon

	Args:
		polygon: A shapely object representing the polygon
		initPos: A shapely point  representing Initial position of the robot
		solverParams: A dict containing solver settings
	Returns:
		chi: Cost chi of coverage of the polygon
	"""

	K1 = 2.0
	K2 = 1.0/radius
	K3 = 360.0

	F1 = K1*polygon.distance(initPos)
	F2 = K2*polygon.area
	F3 = K3*compute_num_contours(polygon=polygon, radius=radius)

	logger.debug("F1: %6.2f F2: %6.2f F3: %6.2f"%(F1, F2, F3))

	return linPenalty*(F1 + F2) + angPenalty*F3


if __name__ == "__main__":

	from shapely.geometry import Polygon
	from shapely.geometry import Point

	P = Polygon([(0, 0), (1, 0), (1, 1), (2, 1), (2, 0), (3, 0), (3, 3), (2, 3), (2, 2), (1, 2), (1, 3), (0, 3)])
	p = Point((0,0))
	#compute_chi(P, p, 1, 1, 1)
	print(compute_num_contours(P, radius=0.1))