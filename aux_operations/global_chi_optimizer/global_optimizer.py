import logging

from decomposition_processing import compute_adjacency
from metrics.chi import compute_chi
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

def chi_reoptimize(decomposition = [],
				   cellToSiteMap = [],
				   originalChiCosts = [],
				   newChiCosts = [],
				   numIterations = 10,
				   radius = 0.1,
				   linPenalty = 1.0,
				   angPenalty = 10*1.0/360):
	"""
	Performs pairwise reoptimization on the poylgon with given robot initial
	position.

	Args:
		decomposition: A set of Shapely polygons representing polygon decomposition.
		cellToSiteMap: A dict mapping cell in the polygon to the starting position of its robot.
		originalChiCosts:  List for storing original costs
		newChiCost: List for storing costs after reoptimization.
		numIterations: The number of iterations or reoptimization cuts to make
		radius: The radius of the coverage footprint
		linPenalty: A parameter used in the cost computation
		angPenalty: A parameter used in the cost computation
	Returns:
		N/A
	"""

	# Store perf stats for monitoring performance of the algorithm. 
	chiCosts = []
	for idx, poly in enumerate(decomposition):
		cost = compute_chi(polygon = Polygon(decomposition[idx]),
							initPos = cellToSiteMap[idx],
							radius = radius,
							linPenalty = linPenalty,
							angPenalty = angPenalty)
		chiCosts.append((idx, cost))

	sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)
	originalChiCosts.extend(sortedChiCosts)

	for i in range(numIterations):
		chiCosts = []
		for idx, poly in enumerate(decomposition):
			cost = compute_chi(polygon = decomposition[idx],
						initPos = cellToSiteMap[idx],
						radius = radius,
						linPenalty = linPenalty,
						angPenalty = angPenalty)
			chiCosts.append((idx, cost))
		sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)

		logger.debug("Iteration: %3d/%3d: Costs: %s"%(i, numIterations, sortedChiCosts))

		adjacencyMatrix = compute_adjacency(decomposition)

		if not dft_recursion(decomposition,
								adjacencyMatrix,
								sortedChiCosts[0][0],
								cellToSiteMap,
								radius,
								linPenalty,
								angPenalty):

			logger.debug("Iteration: %3d/%3d: No cut was made!"%(i, numIterations))


		# Output new sorted costgs
		chiCosts = []
		for idx, poly in enumerate(decomposition):
			cost = compute_chi(polygon = decomposition[idx],
							   initPos = cellToSiteMap[idx],
							   radius = radius,
							   linPenalty = linPenalty,
							   angPenalty = angPenalty)
			chiCosts.append((idx, cost))
		sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)
		newChiCosts.extend(sortedChiCosts)



if __name__ == '__main__':
	from shapely.geometry import Polygon
	from shapely.geometry import Point

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

	chi_reoptimize(decomposition = decomposition,
					cellToSiteMap = q)