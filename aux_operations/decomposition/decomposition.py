import logging

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import nearest_points

# Configure logging properties for this module
logger = logging.getLogger("global_optimizer")
#fileHandler = logging.FileHandler("logs/global_optimizer.log")

streamHandler = logging.StreamHandler()

#logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)


class Decomposition:

    PROXIMITY_THRESHOLD = 1e-5
    """
    Decomposition class for efficient representation of a decomposition.

    Supports the following operations:
    1: Add polygon to the decomposition
    2: Returns a polygon representation associated with an id.
    3: Returns cost for a polygon.
    4. Returns highest cost in the decomposition.
    5. Returns lowest cost in the decomposition.
    6. Returns id of the polygon with the lowest cost in decomp.
    7. Returns id of the polygon with the highest cost in the decomp.
    8. Removes polygon from a decomposition.
    
    Behind the scenes, does the following:
    1. Upon addition of polygon, assigns a unique id.
    2. Upon addition of polygon, computes a metric.
    3. Upon addition of polygon, computes and updates adjacency relations.

    Restrictions:
    1. Only valid and simple polygons are allowed

    """

    def __init__(self, metric=[]):
        self.metric = metric
        self.idCounter = 0
        self.id2Polygon = {}
        self.id2Position = {}
        self.id2Cost = {}
        self.id2Adjacent = {}
        self.sortedCosts = []

    def add_polygon(self, polygon=[], robotPosition=[]):
        """
        Add polygon to the decomposition
        """

        if not polygon.is_valid or not polygon.is_simple:
            return -1

        snappedPolygon = self._snap_to_environment(polygon)

        # Generate a unique id for the polygon
        polygonId = self.idCounter
        self.idCounter += 1

        # Add the polygon to the dictionary
        self.id2Polygon[polygonId] = snappedPolygon
        self.id2Position[polygonId] = robotPosition

        # Compute and record the metric of the polygon
        self.id2Cost[polygonId] = self.metric.compute(polygon=snappedPolygon, initialPosition=robotPosition)

        # Update adjacency dictionary
        self.id2Adjacent[polygonId] = []
        self._update_adjacency(polygonId)

        # Insert the cost into the sort list
        self._insert_cost(polygonId)

        logger.debug("Decomp. dictionary is: {}".format(self.id2Polygon))
        logger.debug("Adjacency dictionary is: {}".format(self.id2Adjacent))

        return polygonId

    def remove_polygon(self, polygonId):
        """
        Remove polygon from the decomposition
        Returns True if remove was succseful
        """

        if polygonId not in self.id2Polygon.keys():
            return False

        del self.id2Polygon[polygonId]
        del self.id2Position[polygonId]
        del self.id2Cost[polygonId]

        # Remove the polygonId from the sorted list. Should only have unique values in here.
        self.sortedCosts.remove(polygonId)

        adjacentPolygonIds = self.id2Adjacent[polygonId]
        for adjPolyId in adjacentPolygonIds:
            self.id2Adjacent[adjPolyId].remove(polygonId)

        del self.id2Adjacent[polygonId]

        return True

    def _insert_cost(self, newPolyId):
        """
        Function for inserting in a sorted manner cost into the sorted array of costs.

        Assumption that cells are stored in this array in the increasing order of the cost.
        """

        if not self.sortedCosts:
            self.sortedCosts.append(newPolyId)
            return

        for idx in range(len(self.sortedCosts)):
            if self.id2Cost[newPolyId] < self.id2Cost[self.sortedCosts[idx]]:
                self.sortedCosts.insert(idx, newPolyId)
                return

        self.sortedCosts.append(newPolyId)

    def _update_adjacency(self, newPolyId):
        """
        Accepts a new polygon and looks for adjacent polygons. Update adjacency dictionary accordingly.
        """

        newPolyDef = self.id2Polygon[newPolyId]
        adjacentPolyIds = [polyId for polyId in self.id2Polygon.keys() if polyId != newPolyId]
        
        for polyId in adjacentPolyIds:

            polygonDef = self.id2Polygon[polyId]
            union = newPolyDef.union(polygonDef)

            if isinstance(union, Polygon) and union.is_valid and union.is_simple:
                self.id2Adjacent[newPolyId].append(polyId)
                self.id2Adjacent[polyId].append(newPolyId)

    def _snap_to_environment(self, newPolygon):
        """
        Due to computational geometry intricacies, the new polygon may be adjacent to other polygons but
        not technically touch each other. In other words, it is within some epsilon distance away from
        adjacent polygons. For our purpose, if polygon is close enough, we can consider it adjacent.
        Such polygons need to be "snapped" to the rest of the polygons.

        Algorithm:
            1) Iterate over polygons in the decomposition and do the following.
            2) Find the nearest point of a polygon from the decomposition to the new polygon.
            3) If the nearest points are verticies of both geometries, just snap the two geometries.
            4) If the nearest points are verticies of polygon from decomposition only, add these
                points to the new polygon and snap.
            5) If the nearest points are verticies of the new polygon only, add these points to the
                polygon from the decomposition and snap.
        """

        originalPolyExterior = newPolygon.exterior.coords[:-1]

        # Step 1: Snap the verticies of the new polygon to the existing environment
        newCoordinates = []
        for id_, otherPolygon in self.id2Polygon.items():
            
            # Avoid doing needless computations for non adjacent polygons
            if otherPolygon.distance(newPolygon) <= self.PROXIMITY_THRESHOLD:

                for point in originalPolyExterior:  # for each vertex in the first polygon
                    p1, p2 = nearest_points(Point(point), otherPolygon)  # find the nearest point on the second polygon
                    if p1.distance(p2) <= self.PROXIMITY_THRESHOLD and \
                        not p1.equals(p2):
                        # it's within the snapping tolerance but 
                        # need to avoid adding duplciates to existing veritcies.
                        if not [True for point_ in newCoordinates if Point(point_).equals(p2)]:
                            newCoordinates.append(p2.coords[0])
                    else:
                        # it's too far, use the original vertex
                        if not [True for point_ in newCoordinates if Point(point_).equals(Point(point))]:
                            newCoordinates.append(point)
        else:
            if not newCoordinates:
                processedPolygon = newPolygon
            else:

                # The coordinates added to the newCoordinates need to be sorted according to their location on the exterior.
                newCoordinates.sort(key=lambda point: newPolygon.exterior.project(Point(point)))
                logger.debug("Snapped veritices: {}".format(newCoordinates))
                # Form a new polygon
                processedPolygon = Polygon(newCoordinates, newPolygon.interiors)

        # Step 2: Snap the verticies of the existing environments to the edges of the new polygon
        newCoordinates = []
        for otherPolygonId, otherPolygon in self.id2Polygon.items():
            
            # Avoid doing needless computations for non adjacent polygons
            if otherPolygon.distance(processedPolygon) <= self.PROXIMITY_THRESHOLD:

                for point in otherPolygon.exterior.coords[:-1]:  # for each vertex in the other polygon
                    p1, p2 = nearest_points(Point(point), processedPolygon)  # find the nearest point on the second polygon
                    if p1.distance(p2) <= self.PROXIMITY_THRESHOLD and \
                       not p1.equals(p2):
                        # it's within the snapping tolerance, use the snapped vertex
                        if not [True for point_ in newCoordinates if Point(point_).equals(p2)]:
                            newCoordinates.append(p2.coords[0])
                    else:
                        # it's too far, use the original vertex
                        if not [True for point_ in newCoordinates if Point(point_).equals(Point(point))]:
                            newCoordinates.append(point)

                processedOtherPolygon = Polygon(newCoordinates, otherPolygon.interiors)
                self.id2Polygon[otherPolygonId] = processedOtherPolygon
                newCoordinates = []

        return processedPolygon
