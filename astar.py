import time
from scipy.spatial import distance

#Return neighbour if inside grid, return None if outside
def _GetNeighbour(node, x, y):
    x += node.parent.x
    y += node.parent.y

    if 0 <= x < len(fullList) and 0 <= y < len(fullList[x]):
        return fullList[x][y].travelNode
    return None

#Return a list of all of the 8 node's neighbours (or less if they're on the edge of the grid)
def _FetchNeighbours(node):
    neighbours = [
        _GetNeighbour(node,-1,0),
        _GetNeighbour(node,1,0),
        _GetNeighbour(node,0,-1),
        _GetNeighbour(node,0,1),
        _GetNeighbour(node,-1,-1),
        _GetNeighbour(node,-1,1),
        _GetNeighbour(node,1,-1),
        _GetNeighbour(node,1,1),
    ]

    #Return None from the list of neighbours
    neighbours = [neighbor for neighbor in neighbours if neighbor is not None]
    return neighbours


def _UpdateNodesNeighbours(node, destination):
    #Go through all of the neighbours of the given node
    for neighbour in _FetchNeighbours(node):
        #Make sure they weren't already visited (picked as the best node in some path)
        if not neighbour.traversable or neighbour in visited:
            continue
        time.sleep(waitTime)
        
        #Calculate the gCost (from start to this node)
        newG = node.CalcGCost(neighbour)

        #If neighbour isn't already queued, we add it to queued
        if neighbour not in queued:
            neighbour.parent.Draw((0,255,0))

            queued.insert(0, neighbour)

            neighbour.cameFrom = node
            neighbour.gCost = newG
            neighbour.hCost = neighbour.CalcHCost(destination)

            neighbour.fCost = neighbour.hCost + neighbour.gCost
        #If it is queued, we update it's gCost and change it's path if this new path is better
        elif neighbour.gCost > newG:
            neighbour.gCost = newG
            neighbour.cameFrom = node

#Go throug all of the queued nodes, and pick the one with the smallest cost
def _PickBestFromQueued():
    if not queued or len(queued) == 0:
        return None

    best = queued[0]
    for node in queued:
        if best.fCost > node.fCost:
            best = node

    time.sleep(waitTime)
    best.parent.Draw((0,0,255))
    queued.remove(best)
    visited.append(best)
    return best

#Once we add a neighbour from the then current best node, we link the neighbour to the then current node making a chain
#We retrace that chain from the destination node, which leads us to the starting node
def _RetracePath(destination):

    #Go back in the link until we reach the beginnig, along the way add change the color of the node's squares to red
    while destination.cameFrom is not None:
        time.sleep(waitTime)
        destination.parent.Draw((255,0,0))
        destination = destination.cameFrom
    destination.parent.Draw((255,0,0))


#The nodes that hold all the necessary information for performing an astar search (besides neighbours, but they arent necessary since this is a grid so it's easy for us to check them)
class TravelNode:
    def __init__(self, parent):
        self.traversable = True
        self.parent = parent
        self.cameFrom = None
        self.gCost = 0
        self.hCost = 0
        self.fCost = 0

    #Calculate the travel cost from starting node to toNode
    def CalcGCost(self, toNode):
        #If toNode is diagonal from selfNode
        if self.parent.x is not toNode.parent.x and self.parent.y is not toNode.parent.y:
            return self.gCost + 1.41
        else:
            return self.gCost + 1
    
    #Calculate the assumed cost from this node to the destination node
    def CalcHCost(self, toNode):
        fromCoords = (self.parent.x, self.parent.y)
        toCoords = (toNode.parent.x, toNode.parent.y)
        return distance.euclidean(fromCoords, toCoords)



waitTime = 0.01

def Search(tileList, originTile, destinationTile, wait):
    #Return if there is no start or end to the search
    if destinationTile is None or originTile is None:
        return None

    #Make the currently searched node the node of the starting tile
    current = originTile.travelNode
    #Make the destination node the node of the ending tile
    destination = destinationTile.travelNode
    #Dont do search if they are the same node
    if current == destination:
        return None

    #Make global variables that will be frequently used by other functions inside this file
    global queued, visited, fullList, waitTime
    waitTime = wait
    queued = [current]
    visited = [current]
    fullList = tileList

    #While we haven't reached the destination, or there is nowhere else to go
    while current != destination and current is not None:
        #Add the current node's neighbours to the queue
        _UpdateNodesNeighbours(current, destination)
        #And pick the best neighbour from the queue
        current = _PickBestFromQueued()

    if current is None:
        return None

    _RetracePath(current)