import logging

from decomposition_processing import compute_adjacency
from metrics.chi import ChiMetric
from recursive_step import dft_recursion

# Configure logging properties for this module
logger = logging.getLogger("global_optimizer")
#fileHandler = logging.FileHandler("logs/global_optimizer.log")

streamHandler = logging.StreamHandler()

#logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.setLevel(logging.INFO)


def _compute_list_costs(decomposition=[], initialPositions=[], metric=[]):
	"""
	Function for computing costs for each cell of the decomposition
	Args:
		decomposition: A set of Shapely polygons representing polygon decomposition.
		cellToSiteMap: A dict mapping cell in the polygon to the starting position of its robot.
		metric: An instance of metric class for computing cut cost.
	Returns:
		sortedCosts: A list of sorted costs
	"""

	# Construct a list of costs.
	costs = []
	for idx, poly in enumerate(decomposition):
		cost = metric.compute(polygon=Polygon(poly), initialPosition=initialPositions[idx])
		costs.append((idx, cost))

	sortedCosts = sorted(costs, key=lambda v:v[1], reverse=True)

	return sortedCosts

def global_optimize(decomposition = [],
				    cellToSiteMap = [],
				    numIterations = 10,
				    metric=[]):
	"""
	Performs pairwise reoptimizations on the cells in the decomposition.

	Args:
		decomposition: A set of Shapely polygons representing polygon decomposition.
		cellToSiteMap: A dict mapping cell in the polygon to the starting position of its robot.
		numIterations: The number of iterations or reoptimization cuts to make
		metric: An instance of metric class for computing cut cost.
	Returns:
		decomposition: New decomposition after the original one was optimized.
		cellToSiteMap: Modifierd cell to site map.
	"""
	
	for i in range(numIterations):
		adjacencyMatrix = compute_adjacency(decomposition)
		
		sortedCosts = _compute_list_costs(decomposition=decomposition,
											initialPositions=cellToSiteMap,
											metric=metric)

		logger.debug("Iteration: %3d/%3d: Costs: %s"%(i, numIterations, sortedCosts))

		if not dft_recursion(decomposition,
								adjacencyMatrix,
								sortedCosts[0][0],
								cellToSiteMap,
								metric):

			logger.debug("Iteration: %3d/%3d: No cut was made!"%(i, numIterations))
	
	return decomposition, cellToSiteMap


if __name__ == '__main__':
	from shapely.geometry import Polygon
	from shapely.geometry import Point

	chi = ChiMetric(radius=0.1, linearPenalty=1.0, angularPenalty=10*1.0/360)

	print("\nSanity tests for the reoptimizer.\n")

	q = [
		Point((0.0,0.0)),
		Point((10.0,0.0)),
		Point((10.0,1.0)),
		Point((0.0,1.0))
		]
	decomposition = [
		Polygon([(0.0,0.0),(10.0,0.0), (10.0,0.5)],[]),
		Polygon([(0.0,0.0),(10.0,0.5),(10.0,1.0),(5.0,0.5)],[]),
		Polygon([(5.0,0.5),(10.0,1.0),(0.0,1.0)],[]),
		Polygon([(0.0,0.0),(5.0,0.5),(0.0,1.0)],[])
	]

	global_optimize(decomposition=decomposition, cellToSiteMap=q, metric=chi)
