import pygame
import astar
import grids
from threading import Thread


class Game:
    def __init__(self, screenSize, squaresInARow):
        if squaresInARow < 20:
            print("Too little squares in a row, please make more than 20 for best effect.")
            return

        pygame.init()
        pygame.display.set_caption("Pathfinding")

        self.screenSizeX = self.screenSizeY = screenSize

        self.screen = pygame.display.set_mode((self.screenSizeX, self.screenSizeY))
        self.screen.fill((255, 255, 255))

        self.mainGrid = grids.SquareGrid(squaresInARow,100, self)

        self.running = True
        self.simulationRunning = False

        #Thread to refresh the screen while gameloop is looping infinitely until game closes
        self.screenThread = Thread(target=RefreshScreen, args=(self,))
        self.screenThread.start()
        self.DoGameLoop()

    def SaveGame(self):
        saveFile = open("save.txt","w")
        saveFile.write(self.mainGrid.ToFileFormat())

    @staticmethod
    def LoadSaveToString():
        savefile = open("save.txt","r")
        return savefile.read()

    def HandleEvents(self):

        #For stopping the simulation/returning to normal functioning after the simulation has ended
        if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
            self.mainGrid.Clear()
            self.simulationRunning = False

        #Checks if quit is waiting in the queue
        if pygame.event.peek(eventtype=pygame.QUIT):
            self.running = False

        #Main events. Don't do anything if simulation is running.
        if not self.simulationRunning:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    #Run the AStar search
                    if pygame.key.get_pressed()[pygame.K_SPACE]:
                        self.simulationRunning = True
                        astar.Search(self.mainGrid.squareList,self.mainGrid.startSquare, self.mainGrid.endSquare, 0.005)
                    #Save the game
                    if pygame.key.get_pressed()[pygame.K_RSHIFT]:
                        self.SaveGame()
                    #Load game from file
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        self.mainGrid.LoadFromString(Game.LoadSaveToString())
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #Make the square traversible or not traversible
                    if event.button == 1:
                        self.mainGrid.ChangeSquareTraversability(pygame.mouse.get_pos())
                    #Make the square normal, starting or ending
                    if event.button == 3:
                        self.mainGrid.ChangeSquareFunction(pygame.mouse.get_pos())

        #Clear the events that are called during a running simulation
        else:
            pygame.event.clear()

    def DoGameLoop(self):
        while self.running:
            self.HandleEvents()
            
        pygame.quit()
    
def RefreshScreen(self):
        while self.running:
            pygame.display.flip()
