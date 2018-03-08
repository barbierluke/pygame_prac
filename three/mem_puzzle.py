# Memory Puzzle
# Al Sweigart
# Simplified BSD license

import random, pygame, sys
from pygame.locals import *

FPS = 30
WINDOW_WIDTH = 640 
WINDOW_HEIGHT = 480
REVEAL_SPEED = 8 # speed boxes' sliding reveals and covers
BOXSIZE = 40 
GAPSIZE = 10 
BOARD_WIDTH = 10 # number of cols of icons
BOARD_HEIGHT = 7 # number of row of icons
assert(BOARD_WIDTH * BOARD_HEIGHT) % 2 == 0, 'Board needs to have an even # of boxes for pairs of matches.'
XMARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOW_HEIGHT - (BOARD_HEIGHT * (BOXSIZE + GAPSIZE))) /2)

# COLOR     R G B
GRAY     = (100, 100, 100)
NAVYBLUE = (060,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

BG_COLOR = NAVYBLUE
LIGHT_BG_COLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHT_COLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)

assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARD_WIDTH * BOARD_HEIGHT, "Board is too big for the number of shapes/colors defined."

def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    mousex = 0 # x coord of mouse event
    mousey = 0 # y coord of mouse event
    pygame.display.set_caption('Memory Game') # This sets the title of the window

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)
    
    firstSelection = None # stores (x,y) of 1st box clicked

    DISPLAYSURF.fill(BG_COLOR)
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False
        DISPLAYSURF.fill(BG_COLOR)
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type = MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # the mouse is currently over a box
            if not revealedBoxex[boxx][boxy]:
                drawHighlightbox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealedBoxesAnimation(mainBoard, [(boxx,boxy)])
                revealedBoxes[boxx][boxy] = True # set the box as 'revealed'
                if firstSelection == None:
                    firstSelection = (boxx,boxy)
                else: # the current box was the 2nd box clicked
                    # check if there is a match between the icons...
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0],firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx,boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections
                        pygame.time.wait(1000) # 1 sec plzzz
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx,boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx, boxy] = False
                    elif hasWon(revealedBoxes):
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # Reset the Board cause we gonna play again
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation
                        startGameAnimation(mainBoard)
                    firstSelection = None # Reset first selection

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARD_WIDTH):
        revealedBoses.append([val] * BOARD_HEIGHT)
    return revealedBoxes
