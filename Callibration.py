import pygame, sys
import math, time
import cv2
from TetrisUtility import *
from PieceMasks import *
import config as c
import PygameButton
from colors import *


PygameButton.init(c.font)


C_BACKDROP = "Background"
C_BOARD = "calliboard"
C_BOARD2 = "calliboard2"
C_NEXT = "nextbox"
C_NEXT2 = "nextbox2"
C_PLAY = "play"
C_PLAY2 = "play2"
C_PAUSE = "pause"
C_PAUSE2 = "pause2"
C_PREVF = "prevframe"
C_PREVF2 = "prevframe2"
C_NEXTF = "nextframe"
C_NEXTF2 = "nextframe2"
C_RENDER = "render"
C_RENDER2 = "render2"
C_SLIDER = "slider"
C_SLIDER2 = "slider2"

C_LVIDEO = "leftvideo"
C_LVIDEO2 = "leftvideo2"
C_RVIDEO = "rightvideo"
C_RVIDEO2 = "rightvideo2"

CALLIBRATION_IMAGES = [C_BACKDROP, C_BOARD, C_BOARD2, C_NEXT, C_NEXT2, C_PLAY, C_PLAY2, C_PAUSE, C_PAUSE2]
CALLIBRATION_IMAGES.extend( [C_PREVF, C_PREVF2, C_NEXTF, C_NEXTF2, C_RENDER, C_RENDER2, C_SLIDER, C_SLIDER2] )
CALLIBRATION_IMAGES.extend([ C_LVIDEO, C_LVIDEO2, C_RVIDEO, C_RVIDEO2 ])
images = loadImages("Images/Callibration/{}.png", CALLIBRATION_IMAGES)

# Image stuff
background = pygame.transform.scale(images[C_BACKDROP], [c.SCREEN_WIDTH, c.SCREEN_HEIGHT])
 # Hydrant-to-Primer scaling factor
hydrantScale = background.get_width() / images[C_BACKDROP].get_width()


class Bounds:

    def __init__(self,isNextBox, x1,y1,x2,y2):

        self.isNB = isNextBox
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.callibration = 1 # 1 = setting top-left point, 2 = setting bottom-right point, 0 = already set
        self.r = 2 if isNextBox else 4

        self.xrlist = None
        self.yrlist = None

        self.directions = [
            [0,0],
            [1,0],
            [-1,0],
            [0,1],
            [0,-1] ]

        if self.isNB:
            self.color = BLUE
            self.horizontal = 8
            self.vertical = 4
            self.Y_TOP = 0.4
            self.Y_BOTTOM = 0.35
            self.X_LEFT = 0.05
            self.X_RIGHT = 0.9
        else:
            self.color = BRIGHT_RED
            self.horizontal = c.NUM_HORIZONTAL_CELLS
            self.vertical = c.NUM_VERTICAL_CELLS
            self.Y_TOP = 0
            self.Y_BOTTOM = 0.993
            self.X_LEFT = 0.01
            self.X_RIGHT = 0.99

        # initialize lookup tables for bounds
        self.updateConversions()

    def updateMouse(self,mx,my):
        
        if self.callibration == 1:
            self.x1 = mx
            self.y1 = my
            self.updateConversions()
        elif self.callibration == 2:
            self.x2 = mx
            self.y2 = my
            self.updateConversions()
        

    def click(self):
        if self.callibration == 1:
            self.callibration = 2
            
        elif self.callibration == 2:
            self.callibration = 0

    # Finalize callibration
    def set(self):
        self.callibration = 0


    def _getPosition(self):
        
        dx = self.X_RIGHT*(self.x2-self.x1) / self.horizontal
        margin = (self.y2-self.y1)*self.Y_TOP
        dy = self.Y_BOTTOM*(self.y2-self.y1-margin) / self.vertical

        # dx, dy, radius
        return dx, dy, (dx+dy)/2/8

    # After change x1/y1/x2/y2, update conversions to scale
    # Generate lookup tables of locations of elements
    def updateConversions(self):
        self.x1s = (self.x1 - c.VIDEO_X) / c.SCALAR
        self.y1s = (self.y1 - c.VIDEO_Y) / c.SCALAR
        self.x2s = (self.x2 - c.VIDEO_X) / c.SCALAR
        self.y2s = (self.y2 - c.VIDEO_Y) / c.SCALAR

        w = self.x2s - self.x1s
        h = self.y2s - self.y1s

        # Generate a list of every x scaled location of the center of all 10 minos in a row
        self.xlist = []
        x = self.x1s + w*self.X_LEFT + w / (self.horizontal*2)
        for i in range(self.horizontal):
            self.xlist.append( int( clamp(x, 0, c.VIDEO_WIDTH) ) )
            x += self.X_RIGHT*(w / self.horizontal)

         # Generate a list of every y scaled location of the center of all 10 minos in a row
        self.ylist = []
        y = self.y1s + w*self.Y_TOP + h / (self.vertical*2)
        for i in range(self.vertical):
            self.ylist.append( int( clamp(y, 0, c.VIDEO_HEIGHT) ) )
            y += self.Y_BOTTOM*(h / self.vertical)

        # xrlist and xylist are an 5-element array of different variants of xlist and ylist.
        # Specifically, they store xlist and ylist offset by radius by different directions.
        # It is precomputed this way for efficiency during each frame.
        # They will be used to quickly get numpy pixels and see if average of each of those 5 points
        #   constitute a filled or empty cell
        self.xrlist = [ self.xlist ]
        self.yrlist = [ self.ylist ]
        for a,b in self.directions: # (a,b) represent some (x,y) offset from the center
            # abbreviated: current x/y list. List comprehension to generate copies of lists with given offset
            self.cxl = [(x+a) for x in self.xlist]
            self.cyl = [(y+b) for y in self.ylist]

            self.xrlist.append(self.cxl)
            self.yrlist.append(self.cyl)


    # Faster replacement for getMinosAndDisplay(). Works directly from nparray.
    # Generates a 2d nparray of minos from nparray of pixels without explicit iteration over each pixel.
    # Called every frame so must be optimized well.
    def getMinos(self, nparray):

        minosList = [] # Represents the 2d arrays of colors at each mino of slightly different offsets from each tetronimo
        for i in range(0,5):
            # colorsList is a [10x20x3] array (vertical x horizontal x rgb] for regular, [4x8x3] for nextbox
            colorsList = nparray[ self.yrlist[0] ][ :  , self.xrlist[0] ]

            # minosVariant is a 10x20 array (4x8 for nextbox), each element representing the average of the rgb values on that pixel for the mino
            minosVariant = np.mean(colorsList, axis = 2)
            minosList.append(minosVariant)

        # np.mean averages all 5 2d arrays. averagedMinosInts is a 10x20 array (4x8 for nextbox), each element the brightness (0-255) of the entire mino
        averagedMinosInts = np.mean(minosList, axis = 0)

        # We use a step function for each element: f(x) = 1 if x >= COLOR_CALLIBRATION else 0
        finalMinos = np.heaviside(averagedMinosInts - c.COLOR_CALLIBRATION, 1) # 1 means borderline case (x = COLOR_CALLIBRATION) still 1

        return finalMinos
        

    # Draw the markings for detected minos.
    def displayBounds(self, surface, nparray = None, minos = None):

        if type(minos) != np.ndarray:
            minos = self.getMinos(nparray)
        
        # draw Red bounds
        pygame.draw.rect(surface, self.color, [self.x1, self.y1, self.x2-self.x1, self.y2-self.y1], width = 2)

        #  Draw cell callibration markers. Start on the center of the first cell

        r = max(1,int(self.r * c.SCALAR))
        for i in range(self.vertical):
                        
            for j in range(self.horizontal):
                
                exists = (minos[i][j] == 1)
                
                x = int(self.xlist[j] * c.SCALAR + c.VIDEO_X)
                y = int(self.ylist[i] * c.SCALAR + c.VIDEO_Y)
                pygame.draw.circle(surface, BRIGHT_GREEN if exists else BRIGHT_RED, [x,y], (r+2) if exists else r, width = (0 if exists else 1))

        return minos

# Slider object during callibration. Move with mousex
class Slider:

    def __init__(self,leftx, y, sliderWidth, startValue, img1, img2):
        self.leftx = leftx
        self.x = self.leftx + startValue * sliderWidth
        self.y = y
        self.width = img1.get_width()
        self.height = img1.get_height()
        self.sliderWidth = sliderWidth
        self.img1 = img1
        self.img2 = img2

        self.SH = 10
        self.active = False
        
    # return float 0-1 indicating position on slider rect
    def tick(self, screen, value, startPress, isPressed, mx, my, animate = False):
        self.hover = self.isHovering(mx,my)
        if startPress and self.hover:
            self.active = True
            
        if isPressed and self.active:
            value =  self.adjust(mx)
        else:
            self.active = False
            if animate:
                self.x = self.leftx + value * self.sliderWidth
            
        self.draw(screen)
        
        return value
            

    def adjust(self,mx):
        self.x = clamp(mx-self.width/2, self.leftx, self.leftx+self.sliderWidth)
        return (self.x - self.leftx) / self.sliderWidth

    def isHovering(self,mx,my):
        return mx >= self.x and mx <= self.x+self.width and my  >= self.y and my <= self.y+self.height

    def draw(self,screen):
        if self.hover:
            screen.blit(self.img2, [self.x, self.y])
        else:
            screen.blit(self.img1, [self.x, self.y])


# Initiates user-callibrated tetris field. Returns currentFrame, bounds, nextBounds for rendering
def callibrate():

    vcap = c.getVideo()
    c.VIDEO_WIDTH = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    c.VIDEO_HEIGHT = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    c.totalFrames = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT))
    c.fps = vcap.get(cv2.CAP_PROP_FPS)
    print("fps: ", c.fps)

    print(c.VIDEO_WIDTH, c.VIDEO_HEIGHT)


    B_CALLIBRATE = 0
    B_NEXTBOX = 1
    B_PLAY = 2
    B_RUN = 3
    B_RENDER = 4
    B_LEFT = 5
    B_RIGHT = 6

    buttons = PygameButton.ButtonHandler()
    buttons.addImage(B_CALLIBRATE, images[C_BOARD], 776, 109, hydrantScale, img2 = images[C_BOARD2])
    buttons.addImage(B_NEXTBOX, images[C_NEXT], 776, 217, hydrantScale, img2 = images[C_NEXT2])
    
    buttons.addImage(B_PLAY, images[C_PLAY], 48,655, hydrantScale, img2 = images[C_PLAY2], alt = images[C_PAUSE], alt2 = images[C_PAUSE2])

    buttons.addImage(B_LEFT, images[C_PREVF], 15, 655, hydrantScale, img2 = images[C_PREVF2])
    buttons.addImage(B_RIGHT, images[C_NEXTF], 73, 655, hydrantScale, img2 = images[C_NEXTF2])
    
    buttons.addImage(B_RENDER, images[C_RENDER], 776, 577, hydrantScale, img2 = images[C_RENDER2])

    
    # Slider stuff
    SW = 320 # slider width
    LEFT_X = 770
    SLIDER_SCALE = 0.47
    sliderImage = scaleImage(images[C_SLIDER], SLIDER_SCALE)
    sliderImage2 = scaleImage(images[C_SLIDER2], SLIDER_SCALE)
    
    colorSlider = Slider(LEFT_X, 345, SW, c.COLOR_CALLIBRATION/255, sliderImage, sliderImage2)
    zoomSlider = Slider(LEFT_X, 465, SW, c.SCALAR, sliderImage, sliderImage2)

    SW2 = 608
    LEFT_X2 = 110
    leftVideoSlider = Slider(LEFT_X2,655, SW2, 0, scaleImage(images[C_LVIDEO],hydrantScale), scaleImage(images[C_LVIDEO2],hydrantScale))
    rightVideoSlider = Slider(LEFT_X2,655, SW2, 1, scaleImage(images[C_RVIDEO],hydrantScale), scaleImage(images[C_RVIDEO2],hydrantScale))

    vidFrame = [0]*2
    LEFT_FRAME = 0
    RIGHT_FRAME = 1
    vidFrame[LEFT_FRAME] = 0
    vidFrame[RIGHT_FRAME] = c.totalFrames - 1
    currentEnd = LEFT_FRAME

    previousFrame = -1

    bounds = None
    nextBounds = None

    minosMain = None # 2d array for main tetris board. 10x20
    minosNext = None # 2d array for lookahead. 8x4

    # seconds to display render error message
    ERROR_TIME = 2

    # for detecting press and release of mouse
    isPressed = False
    wasPressed = False

    errorMsg = None
    
    # Get new frame from opencv
    frame = c.goToFrame(vcap, 0)[0]

    b = buttons.get(B_PLAY)
    
    while True:

        # get mouse position
        mx,my =c.getScaledPos(*pygame.mouse.get_pos())
        isPressed =  pygame.mouse.get_pressed()[0]
        click = wasPressed and not isPressed
        startPress = isPressed and not wasPressed
        buttons.updatePressed(mx,my,click)


        if buttons.get(B_PLAY).clicked:
            
            b.isAlt = not b.isAlt

        if b.isAlt or buttons.get(B_RIGHT).clicked and vidFrame[currentEnd] < c.totalFrames - 1:
            
            frame, vidFrame[currentEnd] = c.goToFrame(vcap, vidFrame[currentEnd] + 1)
                
        elif buttons.get(B_LEFT).clicked and vidFrame[currentEnd] > 0:
            # load previous frame
            frame, vidFrame[currentEnd] = c.goToFrame(vcap, vidFrame[currentEnd] - 1)
         

        c.realscreen.fill([38,38,38])

        # draw backgound
        c.screen.blit(background,[0,0])
            
        surf = c.displayTetrisImage(frame)
        
        if buttons.get(B_CALLIBRATE).clicked:
            bounds = Bounds(False,c.VIDEO_X,c.VIDEO_Y, c.VIDEO_X+surf.get_width(), c.VIDEO_Y+surf.get_height())
            if nextBounds != None:
                nextBounds.set()

        elif buttons.get(B_NEXTBOX).clicked:
            nextBounds = Bounds(True,c.VIDEO_X+surf.get_width()/2, c.VIDEO_Y+surf.get_height()/2,c.VIDEO_X+surf.get_width()/2+50, c.VIDEO_Y+surf.get_height()/2+50)
            if bounds != None:
                bounds.set()

        elif buttons.get(B_RENDER).clicked:

            # If not callibrated, do not allow render
            if bounds == None or nextBounds == None or getNextBox(minosNext) == None:
                errorMsg = time.time()  # display error message by logging time to display for 3 seconds
            
            else:

                print2d(bounds.getMinos(frame))
                print2d(nextBounds.getMinos(frame))
                
                # When everything done, release the capture
                vcap.release()

                # Exit callibration, initiate rendering with returned parameters
                return vidFrame[LEFT_FRAME], vidFrame[RIGHT_FRAME], bounds, nextBounds

        elif click:
            if bounds != None:
                bounds.click()
            if nextBounds != None:
                nextBounds.click()
            
        
        if bounds != None:
            bounds.updateMouse(mx,my)
            minosMain = bounds.displayBounds(c.screen, nparray = frame)

        if nextBounds != None:
            nextBounds.updateMouse(mx,my)
            minosNext = nextBounds.displayBounds(c.screen, nparray = frame)

        # Draw buttons
        buttons.display(c.screen)

        # Draw sliders
        c.COLOR_CALLIBRATION = 150*colorSlider.tick(c.screen, c.COLOR_CALLIBRATION/150, startPress, isPressed, mx, my)
        c.SCALAR = zoomSlider.tick(c.screen, c.SCALAR, startPress, isPressed, mx, my)
        
        # Draw video bounds sliders
        vidFrame[RIGHT_FRAME] = rightVideoSlider.tick(c.screen, vidFrame[RIGHT_FRAME] / (c.totalFrames-1), startPress, isPressed, mx, my,True)
        vidFrame[RIGHT_FRAME] = clamp(int(vidFrame[RIGHT_FRAME] * c.totalFrames),0,c.totalFrames)
        
        vidFrame[LEFT_FRAME]= leftVideoSlider.tick(c.screen, vidFrame[LEFT_FRAME] / (c.totalFrames-1), startPress and not rightVideoSlider.active, isPressed, mx, my,True)
        vidFrame[LEFT_FRAME] = clamp(int(vidFrame[LEFT_FRAME] * c.totalFrames),0,c.totalFrames)
        
        # Update frame from video sliders
        if rightVideoSlider.active:
            currentEnd = RIGHT_FRAME
        elif leftVideoSlider.active:
            currentEnd = LEFT_FRAME
            
        frame, vidFrame[currentEnd] = c.goToFrame(vcap, vidFrame[currentEnd])

        print(vidFrame)

        # Draw timestamp
        text = c.fontbig.render(c.timestamp(vidFrame[currentEnd]), True, WHITE)
        c.screen.blit(text, [840,42] )
        

        # Draw error message
        if errorMsg != None:
            if time.time() - errorMsg < ERROR_TIME:
                text = c.font2.render("You must finish callibrating and go to the first frame to be rendered.", True, RED)
                c.screen.blit(text, [c.SCREEN_WIDTH - 400, 560] )
            else:
                errorMsg = None

        wasPressed = isPressed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                vcap.release()
                pygame.display.quit()
                sys.exit()
                return True
                
            elif event.type == pygame.VIDEORESIZE:
                c.realscreen = pygame.display.set_mode(event.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

        c.handleWindowResize()
            
        pygame.display.update()
