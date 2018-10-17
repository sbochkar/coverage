import logging

from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import LinearRing
from shapely.ops import split
from shapely.ops import snap

SNAP_TOLLERANCE = 1e-05

# Configure logging properties for this module
logger = logging.getLogger("polygonSplit")

#fileHandler = logging.FileHandler("logs/polygonSplit.log")
streamHandler = logging.StreamHandler()

#logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.setLevel(logging.INFO)


def pretty_print_poly(P=[]):
	"""Pretty prints cannonical polygons to help with debugging

	Args:
		P: Polygon in canonical form.

	Returns:
		None
	"""

	print("Polygon:\n\tExterior:\n\t\t"),

	for pts in P[0]:
		# Need to make sure to round some pts for nice display
		print("(%3.1f, %3.1f), "%(pts[0], pts[1])),
	print("")
	holeCnt = 0
	for hole in P[1]:
		print("\tHole %d:\n\t\t"%holeCnt),
		for pts in hole:
			# Need to make sure to round some pts for nice display
			print("(%3.1f, %3.1f),"%(pts[0], pts[1])),
		print("")
		holeCnt += 1


def convert_to_canonical(P=[]):
	"""Convertion function to convert from shapely object to canonical form.

	Args:
		P: Shapely object representing a polygon.

	Returns:
		poly: A polygon represented in canonical form. [] otherwise.
	"""

	if type(P) is not Polygon:
		logger.warn("Polygon conversion requested but wrong input specified.")
		return []

	poly = [[], []]

	if not LinearRing(P.exterior.coords).is_ccw:
		poly[0] = list(P.exterior.coords)[::-1][:-1]
	else:
		poly[0] = list(P.exterior.coords)[:-1]

	for hole in P.interiors:

		if LinearRing(hole.coords).is_ccw:
			poly[1].append(list(hole.coords)[::-1][:-1])
		else:
			poly[1].append(list(hole.coords)[:-1])

	return poly


def polygon_split(polygon=[], splitLine=[]):
	"""Split a polygon into two other polygons along splitLine. This is a wrapper for
	    Shapely split function.

	Attempts to split a polygon into two other polygons.

	Args:
		polygon: Shapely polygon object.
		splitLine: Shapely LineString object.

	Returns:
		(P1, P2): A tuple of Shapely polygons resulted from the split. If error occured,
		returns [].

	"""

	if not splitLine or not polygon or not polygon.is_valid or len(splitLine.coords) != 2:
		return []

	# There is a bazilion ways that the inputs can cause a failure of this method. Rather then
	# spending all of this effort in checking the inputs, I decided to avoid inputs checking and
	# wrap the core algorithm in a try-catch block and only check the validity of the output.
	try:

		snapped = snap(splitLine, polygon.exterior, SNAP_TOLLERANCE)
		result = split(polygon, snapped)

		# Only allow cuts that generate 2 polygons. TODO: Check types of resulting geometries.
		if len(result) == 2:
			return result
		else:
			return []

	except:
		logger.debug("Split was not succseful. Check the validity of the inputs.")
		return []


if __name__ == '__main__':

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.1, 0.1), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1)]])
	e = LineString([(0.05, 0), (0.05, 1)])
	P1, P2 = split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	e = LineString([(1, 0.8), (0.8, 1)])
	P1, P2 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	e = LineString([(0.2, 1), (0, 0.8)])
	P1, P2 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	e = LineString([(0, 0.2), (0.2, 0)])
	P1, P2 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0.1, -0.1)], [])
	e = LineString([(0, 0), (1, 1)])
	P1 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	e = LineString([(0.1, 0.1), (0.9, 0.9)])
	P1 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	e = LineString([(0, 0), (0.9, 0.9)])
	P1 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.4, 1), (0, 1)], [])
	e = LineString([(0.5, 0), (0.5, 1)])
	P1 = polygon_split(P, e)
	print(P1)
