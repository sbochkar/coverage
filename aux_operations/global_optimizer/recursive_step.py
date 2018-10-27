import logging
from numpy import linspace
from itertools import product

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString

from metrics.chi import ChiMetric
from pairwise_optimizer.pairwise_reopt import compute_pairwise_optimal
from decomposition.decomposition import Decomposition

# Configure logging properties for this module
logger = logging.getLogger("recursive_step")
#fileHandler = logging.FileHandler("logs/global_optimizer.log")

streamHandler = logging.StreamHandler()

#logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.setLevel(logging.INFO)


# Need to move these to the main calling function
def dft_recursion(decomposition=[],
				  maxCostPolygonId=0,
				  metric=[]):
	"""
	This is a recursive function that explores all pairs of cells starting with
	one with the highest cost. The purpose is to re-optimize cuts of adjacent
	cells such that the maximum cost over all cells in the map is minimized.

	Params:
		decomposition: A Decomposition object representing decompoisiton of the polygon.
		maxCostPolygonId: Index of a cell in the decomposition with the maximum cost.
		metric: An instance of a metric class for computing the cost of a cut.

	Returns:
		True if a succseful reoptimization was performed. False otherwise.
	"""

	maxPolygonCost = decomposition.id2Cost[maxCostPolygonId]
	logger.debug("Cell %d has maximum cost of : %f"%(maxCostPolygonId, maxPolygonCost))

	surroundingCellIdxs = decomposition.id2Adjacent[maxCostPolygonId]
	logger.debug("Surrounding Cell Idxs: %s"%(surroundingCellIdxs,))

	surroundingChiCosts = [(polygonId, decomposition.id2Cost[polygonId]) for polygonId in surroundingCellIdxs]

	sortedSurroundingChiCosts = sorted(surroundingChiCosts, key=lambda v:v[1], reverse=False)
	logger.debug("Neghbours and chi: %s"%sortedSurroundingChiCosts)

	# Idea: For a given cell with maximum cost, search all the neighbors
	#		and sort them based on their chi cost.
	#
	#		Starting with the neighbor with the lowest cost, attempt to
	#		reoptimize the cut seperating them in hopes of minimizing the max
	#		chi of the two cells.
	#
	#		If the reoptimization was succesful then stop recursion and complete
	#		the iteration.
	#
	#		If the reoptimization was not succesful then it is possible that we
	#		are in a local minimum and we need to disturb the search in hopes
	#		of finiding a better solution.
	#
	#		For that purpose, we call the recursive function on the that
	#		neighboring cell. And so on.
	#
	#		If the recursive function for that neighboring cell does not yield
	#		a reoptimization then we pick the next lowest neighbor and attempt
	#		recursive reoptimization. This ensures DFT of the adjacency graph.

	for cellIdx, cellChiCost in sortedSurroundingChiCosts:

		if cellChiCost < maxPolygonCost:
			logger.debug("Attempting reopt %d and %d."%(maxCostPolygonId, cellIdx))

			result = compute_pairwise_optimal(polygonA=decomposition.id2Polygon[maxCostPolygonId],
											  polygonB=decomposition.id2Polygon[cellIdx],
											  robotAInitPos=decomposition.id2Position[maxCostPolygonId],
											  robotBInitPos=decomposition.id2Position[cellIdx],
											  nrOfSamples=100,
											  metric=metric)

			if result:
				# Resolve cell-robot assignments here.
				# This is to avoid the issue of cell assignments that
				# don't make any sense after polygon cut.
				chiA0 = metric.compute(polygon=result[0], initialPosition=decomposition.id2Position[maxCostPolygonId])
				chiA1 = metric.compute(polygon=result[1], initialPosition=decomposition.id2Position[maxCostPolygonId])
				chiB0 = metric.compute(polygon=result[0], initialPosition=decomposition.id2Position[cellIdx])
				chiB1 = metric.compute(polygon=result[1], initialPosition=decomposition.id2Position[cellIdx])

				maxCostPoint = Point(decomposition.id2Position[maxCostPolygonId])
				cellIdxPoint = Point(decomposition.id2Position[cellIdx])

				decomposition.remove_polygon(maxCostPolygonId)
				decomposition.remove_polygon(cellIdx)

				if max(chiA0, chiB1) <= max(chiA1, chiB0):
					decomposition.add_polygon(polygon=result[0], robotPosition=maxCostPoint)
					decomposition.add_polygon(polygon=result[1], robotPosition=cellIdxPoint)
				else:
					decomposition.add_polygon(polygon=result[0], robotPosition=cellIdxPoint)
					decomposition.add_polygon(polygon=result[1], robotPosition=maxCostPoint)

				logger.debug("Cells %d and %d reopted."%(maxCostPolygonId, cellIdx))

				return True
			else:
				if dft_recursion(decomposition=decomposition,
								 maxCostPolygonId=cellIdx,
								 metric=metric):
					return True
	return False


if __name__ == '__main__':

	print("\nSanity tests for recursive reoptimization.\n")
	chi = ChiMetric(radius=0.1, linearPenalty=1.0, angularPenalty=10*1.0/360)
	decomp = Decomposition(chi)

	decomp.add_polygon(polygon=Polygon([(0.0,0.0),(2.5,0.0),(2.5,1.0),(0.0,1.0)],[]), robotPosition=Point((10,0)))
	decomp.add_polygon(polygon=Polygon([(2.5,0.0),(5.0,0.0),(5.0,1.0),(2.5,1.0)],[]), robotPosition=Point((10,1)))
	decomp.add_polygon(polygon=Polygon([(5.0,0.0),(7.5,0.0),(7.5,1.0),(5.0,1.0)],[]), robotPosition=Point((0,1)))
	decomp.add_polygon(polygon=Polygon([(7.5,0.0),(10.0,0.0),(10.0,1.0),(7.5,1.0)],[]), robotPosition=Point((0,0)))

	print dft_recursion(decomp, 3, chi)
	#result = "PASS" if not dft_recursion(P1, P2, initA, initB) else "FAIL"
	#print("[%s] Simple two polygon test."%result)