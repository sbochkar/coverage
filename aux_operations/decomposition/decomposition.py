from shapely.geometry import Polygon

class Decomposition:
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

        # TODO: Check the validity of the polygon before adding it to the decomposition

        # Generate a unique id for the polygon
        polygonId = self.idCounter
        self.idCounter += 1

        # Add the polygon to the dictionary
        self.id2Polygon[polygonId] = polygon
        self.id2Position[polygonId] = robotPosition

        # Compute and record the metric of the polygon
        self.id2Cost[polygonId] = self.metric.compute(polygon=polygon, initialPosition=robotPosition)

        # Update adjacency dictionary
        self.id2Adjacent[polygonId] = []
        self._update_adjacency(polygonId)

        # Insert the cost into the sort list
        self._insert_cost(polygonId)

        return polygonId

    def remove_polygon(self, polygonId):
        """
        Remove polygon from the decomposition
        """

        pass

    def _insert_cost(self, newPolyId):
        """
        Function for inserting in a sorted manner cost into the sorted array of costs.

        Assumption that cells are stored in this array in the increasing order of the cost.
        """

        if not self.sortedCosts:
            self.sortedCosts.append(newPolyId)
            return

        for idx in range(len(self.sortedCosts)):
            if self.id2Cost[newPolyId] < self.id2Cost[idx]:
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
