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

logger.setLevel(logging.INFO)


class BaseMetric:
	"""
	Base class for Metrics.
	Should not be used by itself.

	Contains compute method which references _compute_metric method of child class.
	"""

	def compute(self, **kwargs):
		return self._compute_metric(**kwargs)


class ChiMetric(BaseMetric):
	"""
	Class for chi metric.
	"""
	
	def __init__(self, radius, linearPenalty, angularPenalty):
		self.radius = radius
		self.linearPenalty = linearPenalty
		self.angularPenalty = angularPenalty

	def _compute_metric(self, polygon, initialPosition):
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
		K2 = 1.0/self.radius
		K3 = 360.0

		F1 = K1*polygon.distance(initialPosition)
		F2 = K2*polygon.area
		F3 = K3*self._compute_num_contours(polygon=polygon, radius=self.radius)

		logger.debug("F1: %6.2f F2: %6.2f F3: %6.2f"%(F1, F2, F3))

		return self.linearPenalty*(F1 + F2) + self.angularPenalty*F3

	def _compute_num_contours(self, polygon=[], radius=1):
		"""
		Computing contours of P.
		TODO: What to do with tiny uncovered areas left
		by turns? For now, count it. Potentially could
		use the area as a check for inclusion.

		Params:
			polygon: A shapely object representing the polygon
			radius: Radius of the coverage implement.
		Returns:
			Number of contours
		"""

		numContours = 0

		# Create a deep copy since we don't want to modify original polygon
		testPolygon = Polygon(polygon.exterior, polygon.interiors)
		while not testPolygon.is_empty:

			if isinstance(testPolygon, Polygon):
				numHoles = len(testPolygon.interiors)
				numContours += 1 + numHoles

			elif isinstance(testPolygon, MultiPolygon):
				numContours += len(testPolygon)

				for poly in testPolygon:
					numContours += len(poly.interiors)

			# TODO: Analyze the effects of join_styles
			testPolygon = testPolygon.buffer(-radius)
			
		logger.debug("Number of contours: %d"%numContours)

		return numContours


if __name__ == "__main__":

	from shapely.geometry import Polygon
	from shapely.geometry import Point

	P = Polygon([(0, 0), (1, 0), (1, 1.3), (2, 1.3), (2, 0), (3, 0), (3, 3), (2, 3), (2, 1.7), (1, 1.7), (1, 3), (0, 3)])
	p = Point((0,0))

	chi = ChiMetric(radius=0.1, linearPenalty=1.0, angularPenalty=1.0)
	print(chi.compute(polygon=P, initialPosition=p))
