import logging

from decomposition.decomposition import Decomposition
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


def global_optimize(decomposition = [],
				    numIterations = 10,
				    metric=[]):
	"""
	Performs pairwise reoptimizations on the cells in the decomposition.

	Args:
		decomposition: A Decomposition object representing decomposition of the polygon.
		numIterations: The number of iterations or reoptimization cuts to make
		metric: An instance of metric class for computing cut cost.
	Returns:
		decomposition: New decomposition after the original one was optimized.
	"""
	
	for i in range(numIterations):
		logger.debug("Iteration: %3d/%3d"%(i, numIterations))

		if not dft_recursion(decomposition, decomposition.sortedCosts[-1], metric):
			logger.debug("Iteration: %3d/%3d: No cut was made!"%(i, numIterations))
	
	return decomposition


if __name__ == '__main__':
	from shapely.geometry import Polygon
	from shapely.geometry import Point

	chi = ChiMetric(radius=0.1, linearPenalty=1.0, angularPenalty=10*1.0/360)
	decomp = Decomposition(chi)

	# decomp.add_polygon(polygon=Polygon([(0.0,0.0),(10.0,0.0),(10.0,0.5)],[]), robotPosition=Point((0.0,0.0)))
	# decomp.add_polygon(polygon=Polygon([(0.0,0.0),(10.0,0.5),(10.0,1.0),(5.0,0.5)],[]), robotPosition=Point((10.0,0.0)))
	# decomp.add_polygon(polygon=Polygon([(5.0,0.5),(10.0,1.0),(0.0,1.0)],[]), robotPosition=Point((10.0,1.0)))
	# decomp.add_polygon(polygon=Polygon([(0.0,0.0),(5.0,0.5),(0.0,1.0)],[]), robotPosition=Point((0.0,1.0)))


	decomp.add_polygon(polygon=Polygon([(0.0,0.0),(4.0,0.0),(4.0,4.0),(6.0,4.0),(5.0, 5.0),(0.0, 4.0)],[]), robotPosition=Point((10,0)))
	decomp.add_polygon(polygon=Polygon([(6.0,4.0),(6.0,0.0),(10.0,0.0),(10.0,6.0),(8.0,7.0),(5.0,5.0)],[]), robotPosition=Point((10,10)))
	decomp.add_polygon(polygon=Polygon([(7.5,8.0),(10.0,7.5),(10.0,10.0),(0.0,10.0),(0.0,5.0),(5.0,6.0)],[]), robotPosition=Point((0,10)))
	decomp.add_polygon(polygon=Polygon([(5.0,5.0),(8.0,7.0),(7.5,8.0),(5.0,6.0)],[]), robotPosition=Point((0,0)))


	# decomp.add_polygon(polygon=Polygon([(0,0),(10,0),(10,2),(0,2)],[]), robotPosition=Point((0,0)))
	# decomp.add_polygon(polygon=Polygon([(0,2),(5,2),(5,4),(0,4)],[]), robotPosition=Point((0,2)))
	# decomp.add_polygon(polygon=Polygon([(5,2),(10,2),(10,4),(5,4)],[]), robotPosition=Point((5,2)))


	# decomp.add_polygon(polygon=Polygon([(0,0),(10,0),(10,2),(0,1)],[]), robotPosition=Point((0,0)))
	# decomp.add_polygon(polygon=Polygon([(0,1),(5,1.5),(0,4)],[]), robotPosition=Point((0,2)))
	# decomp.add_polygon(polygon=Polygon([(5,1.5),(10,2),(10,4),(0,4)],[]), robotPosition=Point((5,2)))

	print("\nSanity tests for the reoptimizer.\n")

	global_optimize(decomposition=decomp, metric=chi, numIterations=10)
	from visuals.coverage_plot import *
	ax = init_axis()
	plot_decomposition(ax, decomp)
	display()

