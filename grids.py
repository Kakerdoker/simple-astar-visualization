import pygame
import astar
import re

class Square:
    def __init__(self, coords, parentGrid, isStart = False, isEnd = False):
        self.x = coords[0]
        self.y = coords[1]

        self.parentGrid = parentGrid
        self.size = parentGrid.squareSize
        screenPosition = self.parentGrid.CalculateScreenPosition((self.x,self.y))

        self.screenX = screenPosition[0]
        self.screenY = screenPosition[1]

        self.travelNode = astar.TravelNode(self)

        self.isStart = False
        self.isEnd = False

        if isStart == True:
            self._MakeStart()
        elif isEnd == True:
            self._MakeEnd()
        else: 
            self.Draw((255,255,255))

    #Returns the important data for saving and loading squares as a string object.
    def ToFileFormat(self):
        return "{"+f"{self.travelNode.traversable},{self.isStart},{self.isEnd}"+"}"

    #If the square is normal, then it becomes a starting square
    #If the square is a starting square, then it becomes an ending square
    #If the square is an ending square, the square becomes normal
    def RotateBetweenStartEndNormal(self):
        if not self.travelNode.traversable:
            return
        
        if not self.isStart and not self.isEnd:
            self._MakeStart()
        elif self.isStart:
            self._MakeEnd()
        elif self.isEnd:
            self.MakeNormal()
    
    #Make the square into a normal one (is traversable, is neither the start nor the ending position)
    def MakeNormal(self):
        if self.parentGrid.endSquare is self:
            self.parentGrid.endSquare = None
        if self.parentGrid.startSquare is self:
            self.parentGrid.startSquare = None
        
        self.isStart = False
        self.isEnd = False
        self.Draw((255,255,255))

    #Make the square the ending position
    def _MakeEnd(self):
        if self.parentGrid.endSquare is not None:
            self.parentGrid.endSquare.MakeNormal()

        self.parentGrid.endSquare = self
        self.isStart = False
        self.isEnd = True
        self.Draw((0, 255, 255))

    #Make the square the starting position
    def _MakeStart(self):
        if self.parentGrid.startSquare is not None and self.parentGrid.startSquare is not self.parentGrid.endSquare:
            self.parentGrid.startSquare.MakeNormal()

        self.parentGrid.startSquare = self
        self.isStart = True
        self.isEnd = False
        self.Draw((255, 0, 255))

    #Make the square traversible if it isn't or not traversible if it is
    def ChangeTraversability(self):
        if self.isStart or self.isEnd:
            return

        self.travelNode.traversable = not self.travelNode.traversable
        if self.travelNode.traversable:
            self.Draw((255,255,255))
        else:
            self.Draw((55,55,55))

    #Returns the square to its original color
    def Clear(self):
        if self.travelNode.traversable:
            if self.isStart == True:
                self.Draw((255, 0, 255))
            elif self.isEnd == True:
                self.Draw((0, 255, 255))
            else:
                self.Draw((255,255,255))

    #Draws the square with the given color
    def Draw(self, color):
        pygame.draw.rect(self.parentGrid.parentGame.screen, color, (self.screenX, self.screenY, self.size, self.size), 0)
        pygame.draw.rect(self.parentGrid.parentGame.screen, (0,0,0), (self.screenX, self.screenY, self.size, self.size), 2)
    

class SquareGrid:

    #Initialize all of the varaibles used within SquareGrid
    def _InitializeVariables(self, squaresInARow, margin, parentGame):
        self.squaresInARow = squaresInARow
        self.margin = margin
        self.parentGame = parentGame
        self.gridSizeX = self.gridSizeY = parentGame.screenSizeX - (2 * self.margin)
        self.squareSize = parentGame.screenSizeX//squaresInARow
        self.squareAmount = (self.gridSizeX // self.squareSize)

        self.startSquare = None
        self.endSquare = None

    #Creates a N by N grid of normal traversible squares
    def _CreateEmptyGrid(self):
        self.squareList = []
        for x in range(self.squareAmount):
            self.squareList.append([])
            for y in range(self.squareAmount):
                self.squareList[x].append(Square((x,y), self))

    def __init__(self, squaresInARow, margin, parentGame):
        self._InitializeVariables(squaresInARow, margin, parentGame)
        self._CreateEmptyGrid()
        
    #Takes the given string as an argument and draws a grid using data from that string
    def LoadFromString(self, string):

        #Unpack the string into a usable object
        data = re.search(r"\{(.+)}$", string)
        if data:
            squareValList = data[1]
            squareValList = squareValList.replace("{", "[").replace("}", "]")
            squareValList = eval(squareValList)

        #Initialize all the necessary variables with the loaded squaresInARow variable
        squaresInARow = int(squareValList[0])
        self._InitializeVariables(squaresInARow, self.margin, self.parentGame)

        #Go through the remaining data, and initiate new squares using it.
        y = -1
        x = 0
        self.squareList = []
        #Starting from 1 because the first value is >squaresInARow<
        for i in range(1,len(squareValList)):
            x = i-1
            self.squareList.append([])
            for y in range(len(squareValList[i])):
                #squareValList[i][y][0] checks if the square is traversable
                #squareValList[i][y][1] checks if the square is the starting square
                #squareValList[i][y][2] checks if the square is the ending square
                
                self.squareList[x].append(Square((x,y),self, isStart = squareValList[i][y][1], isEnd = squareValList[i][y][2]))
                #change traversability only if it is false, since a normal square starts as traversible
                if squareValList[i][y][0] == False:
                    self.squareList[x][y].ChangeTraversability()
    
    #Returns all of its necessary information in a string format
    def ToFileFormat(self):
        string = "{"+f"{self.squaresInARow},"

        for column in self.squareList:
            string += "{"
            for square in column:
                string += square.ToFileFormat() + ","
            string += "},"
        string += "}"

        return string
    
    #Calculates the square coordinates on screen from coordinates inside the grid
    def CalculateScreenPosition(self, coords = (0,0)):
        __screenX = coords[0]*self.squareSize + (self.margin)
        __screenY = coords[1]*self.squareSize + (self.margin)
        return (__screenX, __screenY)
    
    #Calculates the coordinates inside the squareList from coordinates on the screen
    def _GetCoordinatesFromScreen(self, coords = (0,0)):
        __x = (coords[0] - (self.margin)) // self.squareSize
        __y = (coords[1] - (self.margin)) // self.squareSize
        return (__x, __y)
    
    #Checks whether the given screen coordinates are inside the grid holding the squares
    def IsInsideGrid(self, screenCoords):
        x = screenCoords[0]
        y = screenCoords[1]
        if x < self.margin or y < self.margin:
            return False
        if x > self.gridSizeX+self.margin or y > self.gridSizeY+self.margin:
            return False
        return True

    #Changes the traversability of the square on the given screen coordinates (if it exists)
    def ChangeSquareTraversability(self, screenCoords):
        if self.IsInsideGrid(screenCoords):
            x,y = self._GetCoordinatesFromScreen(screenCoords)
            self.squareList[x][y].ChangeTraversability()
    
    #Changes the function of the square (is end, is start, is normal) on the given screen coordinates (if it exists)
    def ChangeSquareFunction(self, screenCoords):
        if self.IsInsideGrid(screenCoords):
            x,y = self._GetCoordinatesFromScreen(screenCoords)
            self.squareList[x][y].RotateBetweenStartEndNormal()
        
    #Goes through all of the squares and changes their color to their original
    def Clear(self):
        for columns in self.squareList:
            for square in columns:
                square.Clear()
                    

