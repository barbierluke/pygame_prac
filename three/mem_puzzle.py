# Memory Puzzle
# Al Sweigart
# Simplified BSD license

import random, pygame, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640 
WINDOWHEIGHT = 480
REVEALSPEED = 8 # speed boxes' sliding reveals and covers
BOXSIZE = 40 
GAPSIZE = 10 
BRD_NUM_COLS = 6
BRD_NUM_ROWS = 4
assert(BRD_NUM_COLS * BRD_NUM_ROWS) % 2 == 0, 'Board needs to have an even # of boxes for pairs of matches.'
XMARGIN = int((WINDOWWIDTH - (BRD_NUM_COLS * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BRD_NUM_ROWS * (BOXSIZE + GAPSIZE))) /2)

# COLOR     R G B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)

assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BRD_NUM_COLS * BRD_NUM_ROWS, "Board is too big for the number of shapes/colors defined."

def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0 # x coord of mouse event
    mousey = 0 # y coord of mouse event
    pygame.display.set_caption('Memory Game') # This sets the title of the window

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False) # just returns a list of lists of boolean falses
    
    firstSelection = None # stores (x,y) of 1st box clicked

    DISPLAYSURF.fill(BGCOLOR) # background color
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # the mouse is currently over a box
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx,boxy)])
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
                        revealedBoxes[boxx][boxy] = False
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

# Understand it
def generateRevealedBoxesData(val):
    # just returns a list of column lists of booleans True or False
    revealedBoxes = []
    for i in range(BRD_NUM_COLS):
        revealedBoxes.append([val] * BRD_NUM_ROWS)
    return revealedBoxes

# Understand it
def getRandomizedBoard():
    # Get a list of every possible shape and color
    icons = []
    for color in ALLCOLORS:
        for shape in ALLSHAPES:
            icons.append((shape,color))
        
    random.shuffle(icons)
    numIconsUsed= int(BRD_NUM_COLS * BRD_NUM_ROWS / 2) # how many icons needed
    icons = icons[:numIconsUsed] * 2
    random.shuffle(icons)

    # Create Board data Structure, with randomly placed icons
    # Is board DS just a list of the columns of icons
    board = []
    for x in range(BRD_NUM_COLS):
        column = []
        for y in range(BRD_NUM_ROWS):
            column.append(icons[0])
            del icons[0]
        board.append(column)
    return board # just a list of shape and color tuples

# Understand it
def splitIntoGroupsOf(groupSize, theList):
    # splits the list into sublists of size groupSize
    result = []
    for i in range(0,len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result

# Understand it
def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top  = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)

# Understand it
# We're just getting the rectangle where the click happened
def getBoxAtPixel(x,y):
    for boxx in range(BRD_NUM_COLS):
        for boxy in range(BRD_NUM_ROWS):
            left, top = leftTopCoordsOfBox(boxx,boxy)
            boxRect = pygame.Rect(left,top,BOXSIZE,BOXSIZE)
            if boxRect.collidepoint(x,y): # test if a point is inside the rectangle :)
                return (boxx,boxy)
    return (None, None)

# Just figure out which icon it is and draw it with a simple if statement
def drawIcon(shape,color,boxx,boxy):
    quarter = int(BOXSIZE * 0.25)
    half = int(BOXSIZE * 0.5)

    left,top = leftTopCoordsOfBox(boxx,boxy)

    # Drawin shapes apparently
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURF, color, (left + i, top + BOXSIZE - 1), (left + BOXSIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))

def getShapeAndColor(board, boxx, boxy):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[boxx][boxy][0], board[boxx][boxy][1]

def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)
    
def revealBoxesAnimation(board, boxesToReveal):
    # Do the "box reveal" animation.
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, - REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)

def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED): # range(start,stop,iterator)
        drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(BRD_NUM_COLS):
        for boxy in range(BRD_NUM_ROWS):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                # Draw the (revealed) icon
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)

def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

# 
def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False) # empty list of list of boolean false values
    boxes = [] # just a list of tuples...[[1,1],[1,2],[1,3]..[2,1],[2,2]...]
    for x in range(BRD_NUM_COLS):
        for y in range(BRD_NUM_ROWS):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)
    
    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

# Just flash the screen 13 times...
def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR
    
    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)

# Understand it
def hasWon(revealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False # return False if any boxes are covered.
    return True

if __name__ == '__main__':
    main()
