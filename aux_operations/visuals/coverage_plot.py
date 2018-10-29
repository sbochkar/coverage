import matplotlib.pyplot as plt

from shapely.geometry import Polygon
from descartes import PolygonPatch

from decomposition.decomposition import Decomposition


COLOR_LIST = [
	'#000000',
 	'#FFFFFF',
 	'#FF0000',
 	'#00FF00',
 	'#0000FF',
 	'#FFFF00',
 	'#00FFFF',
 	'#FF00FF',
 	'#C0C0C0',
 	'#808080',
 	'#800000',
 	'#808000',
 	'#008000',
 	'#800080',
 	'#000080',
	'#008080'
]
def init_axis(title = '', geometry = ''):
	"""
	Initializes plotting area and returns a handle for plot area
	:param None:
	:return: Axis object
	"""

	fig = plt.figure()
	ax = fig.add_subplot(111)
	plt.axis("equal")

	mngr = plt.get_current_fig_manager()
	#mngr.window.setGeometry(50,100,640, 545)
	mngr.window.wm_geometry(geometry)

	ax.get_yaxis().set_ticks([])
	ax.get_xaxis().set_ticks([])

	ax.set_title(title)

	return ax


def plot_polygon_outline(ax, polygon, fcIdx = 0):
	"""
	Function will plot the ouline of polygon. No decomposition.
	Adjust the axis as well.
	:param ax: Axis object for redundancy
	:param polygon: Possibly with holes
	:return: None
	"""

	colors = ["#00FD91", "#1472FD","#FFA100", "#FF4900"]
	#color_id = ["white","green","red","blue","yellow","pink"]

	min_x, min_y, max_x, max_y = polygon.bounds

	patch = PolygonPatch(polygon,
						 alpha = 1,
						 fc = colors[fcIdx],
						 ec = 'black',
						 linewidth = 3,
						 linestyle = 'solid',
						 zorder = 2,
						 fill = False,
						 facecolor = "#6699cc",
						 edgecolor = "#6699cc")
	
	ax.add_patch(patch)
	ax.set_xlim([min_x-0.5,max_x+0.5])
	ax.set_ylim([min_y-0.5,max_y+0.5])


def plot_decomposition(ax, decomposition):
	"""
	Function plots a decomposition (aka a list of polygons)
	:param ax: Axis object for redundancy
	:param decomposition: A list of polygons comprosing a decomposition
	:return: None
	"""

	# Plot individual cells
	for i, polygon in decomposition.id2Polygon.items():

		x, y = polygon.exterior.xy

		ax.plot(x,
				y,
				color = COLOR_LIST[i%16],
				alpha = 0.7,
				linewidth = 3,
				solid_capstyle = 'round',
				zorder = 1)

		centroid = polygon.centroid
		ax.annotate(i, (centroid.x, centroid.y))


def plot_init_pos_and_assignment(ax, decomposition):
	"""
	Function plots initial positions of the robots
	:param ax: Axis object for redundancy
	:param decomposition: A list of polygons comprosing a decomposition
	:return: None
	"""

	colors = ["#00FD91", "#1472FD","#FFA100", "#FF4900"]
	for idx, position in decomposition.id2Position.items():
		
		polygon = decomposition.id2Polygon[idx]
		x, y = polygon.exterior.xy

		# Fist plot the initial position as dots
		ax.scatter(*position,
					color = colors[idx],
					alpha = 0.9,
					linewidth = 10,
					zorder = 1)	
		# Then plot the barely visible patches representing
		#	assignments.
		patch = PolygonPatch(polygon,
							 alpha = 0.1,
						 	 fc = colors[idx],
						 	 ec = '#6699cc',
						 	 linewidth = 3,
						 	 linestyle = 'solid',
						 	 zorder = 1,
						 	 fill = True)
		ax.add_patch(patch)


def plot_main_polygon(ax, P):
	"""
	Function will plot the ouline of cleaning area. No decomposition.
	Adjust the axis as well.
	:param ax: Axis object for redundancy
	:param polygon: Possibly with holes
	:return: None
	"""

	min_x, min_y, max_x, max_y = P.bounds

	patch = PolygonPatch(P, alpha=0.9, fc='white', ec='black', linewidth=5, zorder=1, capstyle='round', fill=False, joinstyle='round') # facecolor="#6699cc", edgecolor="#6699cc", alpha=0.5, zorder=1)
	ax.add_patch(patch)
	#x, y= P.xy
	#ax.plot(x,y)
	ax.set_xlim([min_x-0.5,max_x+0.5])
	ax.set_ylim([min_y-0.5,max_y+0.5])


def plot_init_poss(ax, segments):
	ax.scatter(*zip(*segments), color='blue', alpha=0.9, linewidth=10, zorder=1)	

	#ax.relim()
	# update ax.viewLim using the new dataLim
	ax.autoscale()


def plot_samples(ax, segments, idx=0):
	"""
	Function will plot the samples inside the cvx sets
	:param ax: Axis object
	:param lines: List of lines for each convex set
	:return: None
	"""

	import classes
	colors = ["#00FD91", "#1472FD","#FFA100", "#FF4900"]
	for segment in segments:
		if isinstance(segment, classes.PointSegment):
			x, y = segment.coord
			#ax.scatter(x, y, color='orange', alpha=0.9, linewidth=1, zorder=3)	
			ax.scatter(x, y, color=colors[idx], alpha=0.8, linewidth=1, zorder=3)	
		elif isinstance(segment, classes.LineSegment):
			x, y = zip(*segment.coords)
			#ax.plot(x, y, color='orange', alpha=0.9, linewidth=3, zorder=3)	
			ax.plot(x, y, color=colors[idx], alpha=0.8, linewidth=2, zorder=3)	


def plot_grid(ax, grid):
	"""
	Function will plot the samples inside the cvx sets
	:param ax: Axis object
	:param lines: List of lines for each convex set
	:return: None
	"""
	ax.scatter(zip(*grid)[0], zip(*grid)[1])


def plot_grid_tour(ax, grid, tour, next_mtx):

	def return_path(u, v, next_mtr):
		"""
		This function will return a path between a pair
		of verticies
		:param u: 1st vertex
		:param v: 2nd vertex
		:param next_mtr: path tree
		"""
		if next_mtr[u][v] is None:
			return []

		path = [u]

		while u != v:
			u = next_mtr[u][v]
			path.append(u)

		return path 

	NUM_NODES_IN_CLUSTER = 8
	path = []

	path.append(grid[tour[0]])
	for i in range(1, len(tour)):
		ver_out = tour[i-1]
		ver_in = tour[i]

		destination_path = return_path(ver_out, ver_in, next_mtx)

		if (len(destination_path)>2):
			for i in range(1, len(destination_path)):
				node_out = destination_path[i-1]/NUM_NODES_IN_CLUSTER
				node_in = destination_path[i]/NUM_NODES_IN_CLUSTER

				path.append(grid[node_in])

				x = zip(*[grid[node_out], grid[node_in]])[0]
				y = zip(*[grid[node_out], grid[node_in]])[1]
				ax.plot(x, y, color='red', linewidth=2)
			
		else:
			node_out = ver_out/NUM_NODES_IN_CLUSTER
			node_in = ver_in/NUM_NODES_IN_CLUSTER
			path.append(grid[node_in])

			x = zip(*[grid[node_out], grid[node_in]])[0]
			y = zip(*[grid[node_out], grid[node_in]])[1]
			ax.plot(x, y, color='black', linewidth=1)


def plot_tour(ax, tour, lines, dict_map):
	"""
	Function will plot the GTSP tour.
	:param ax:
	:param tour: tour
	:param lines:
	:param dict_map: 
	"""

	for i in range(len(tour)-1):
		o_node = tour[i]
		i_node = tour[i+1]

		o_poly_idx, o_line_idx, o_dirr_idx = dict_map[o_node]
		i_poly_idx, i_line_idx, i_dirr_idx = dict_map[i_node]

		o_pt = lines[o_poly_idx][o_line_idx][o_dirr_idx]
		i_pt = lines[i_poly_idx][i_line_idx][(1+i_dirr_idx)%2]

		dx = i_pt[0] - o_pt[0]
		dy = i_pt[1] - o_pt[1]

		ax.arrow(o_pt[0], o_pt[1], dx, dy, head_width=0.1, ec='green', length_includes_head=True, zorder=4)


def plot_tour_dubins(ax, tour, dict_map, r, idx=0):
	"""
	Function will plot the GTSP tour.
	:param ax:
	:param tour: tour
	:param lines:
	:param dict_map: 
	"""

	import math
	import dubins
	colors = ["#00FD91", "#1472FD","#FFA100", "#FF4900"]
	n = len(tour)
	for i in range(len(tour)):
		outgoing_node_idx = tour[i]
		incoming_node_idx = tour[(i+1)%n]

		outgoing_segment, dir_o = dict_map[outgoing_node_idx]
		incoming_segment, dir_i = dict_map[incoming_node_idx]

		q0 = outgoing_segment.get_exit_info(dir_o)
		q1 = incoming_segment.get_entrance_info(dir_i)
		smpls, _ = dubins.path_sample(q0, q1, r, 0.05)

		x = []
		y = []
		xarrow = 0
		yarrow = 0
		for smpl in smpls:
			xt, yt, at = smpl
			x.append(xt)
			y.append(yt)

			if len(x) == int(math.floor(len(smpls)/2)):
				# Insert arrow mid way through dubins curve
				xarrow = x[int(math.floor(len(smpls)/2))-2]
				yarrow = y[int(math.floor(len(smpls)/2))-2]

				dx = x[int(math.floor(len(smpls)/2))-1] - x[int(math.floor(len(smpls)/2))-2]
				dy = y[int(math.floor(len(smpls)/2))-1] - y[int(math.floor(len(smpls)/2))-2]


		#ax.scatter(x, y, s=0.4, color='green', zorder=4)
		ax.scatter(x, y, alpha=1, s=0.4, color=colors[idx], linewidth=1, zorder=4)
		#dx = i_pt[0] - o_pt[0]
		#dy = i_pt[1] - o_pt[1]

		#ax.arrow(xarrow, yarrow, dx, dy, head_width=0.15, ec='green', length_includes_head=True, zorder=4)


def update(ax):
	ax.canvas.draw()


def display():
	"""
	Function display the figure
	:return: None
	"""

	plt.show()

