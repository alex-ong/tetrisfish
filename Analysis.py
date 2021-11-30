import pygame, sys, math
import AnalysisBoard
import config as c
from Position import Position
import PygameButton
from colors import *
from PieceMasks import *
import HitboxTracker as HT
from TetrisUtility import loadImages
import EvalGraph
import AnalysisConstants as AC

class EvalBar:

    def __init__(self):
        self.currentPercent = 0
        self.targetPercent = 0
        self.currentColor = WHITE

    def tick(self, target, targetColor):
        self.targetPercent = target

        # "Approach" the targetPercent with a cool slow-down animation
        self.currentPercent += math.tanh((self.targetPercent - self.currentPercent))/9
        self.currentColor = [(current + (target-current)*0.13) for (current, target) in zip(self.currentColor, targetColor)]

    # percent 0-1, 1 is filled
    def drawEval(self):

        
        width = 100
        height = 1365
        surf = pygame.Surface([width, height])
        surf.fill(DARK_GREY)
        

        sheight = int((1-self.currentPercent) * height)
        pygame.draw.rect(surf, self.currentColor, [0,sheight, width, height - sheight])

        return surf
    
def analyze(positionDatabase, hzInt):
    global realscreen

    print("START ANALYSIS")


    IMAGE_NAMES = [BOARD, CURRENT, NEXT, PANEL]
    IMAGE_NAMES.extend( [LEFTARROW, RIGHTARROW, LEFTARROW2, RIGHTARROW2, STRIPES ])
    IMAGE_NAMES.extend( [LEFTARROW_MAX, RIGHTARROW_MAX, LEFTARROW2_MAX, RIGHTARROW2_MAX] )

    # Load all images.
    images = loadImages("Images/Analysis/{}.png", IMAGE_NAMES)

    bigMinoImages = []
    # Load mino images for all levels
    for i in range(0,10):
        bigMinoImages.append(loadImages("Images/Analysis/Minos/" + str(i) + "/{}.png", MINO_COLORS))
    
    AnalysisBoard.init(images, bigMinoImages)

    evalBar = EvalBar()

    B_LEFT = "LeftArrow"
    B_RIGHT = "RightArrow"
    B_MAXLEFT = "LeftArrowFast"
    B_MAXRIGHT = "RightArrowFast"
    B_HYP_LEFT = "LeftArrowHypothetical"
    B_HYP_RIGHT = "RightArrowHypothetical"
    B_HYP_MAXLEFT = "MaxLeftArrowHypothetical"
    B_HYP_MAXRIGHT = "MaxRightArrowHypothetical"

    
    buttons = PygameButton.ButtonHandler()
    # Position buttons
    y = 800
    buttons.addImage(B_LEFT, images[LEFTARROW], 950, y, 0.3, margin = 5, alt = images[LEFTARROW2])
    buttons.addImage(B_RIGHT, images[RIGHTARROW], 1150, y, 0.3, margin = 5, alt = images[RIGHTARROW2])

    # Hypothetical positon navigation buttons
    x = 910
    y = 360
    buttons.addImage(B_HYP_MAXLEFT, images[LEFTARROW_MAX], x, y, 0.16, margin = 0, alt = images[LEFTARROW2_MAX])
    buttons.addImage(B_HYP_LEFT, images[LEFTARROW], x+100, y, 0.16, margin = 0, alt = images[LEFTARROW2])
    buttons.addImage(B_HYP_RIGHT, images[RIGHTARROW], x+180, y, 0.16, margin = 0, alt = images[RIGHTARROW2])
    buttons.addImage(B_HYP_MAXRIGHT, images[RIGHTARROW_MAX], x+260, y, 0.16, margin = 0, alt = images[RIGHTARROW2_MAX])
    

    positionNum = 0
    analysisBoard = AnalysisBoard.AnalysisBoard(positionDatabase)

    # Setup graph
    evals = [position.evaluation for position in positionDatabase]

    print("Evals: ", evals)
    
    
    levels = [position.level for position in positionDatabase]
    #TESTLEVELS = [18]*500 + [19] * 500
    #testEvals = [max(0, min(1, np.random.normal(loc = 0.5, scale = 0.2))) for i in range(len(levels))]

    # CALCULATE BRILLANCIES/BLUNDERS/ETC HERE. For now, test code
    #testFeedback = [AC.NONE] * len(levels)
    #for i in range(30):
    #    testFeedback[random.randint(0,len(levels)-1)] = random.choice(list(AC.feedbackColors))

    feedback = [AC.NONE] * len(levels)
    for i in range(len(positionDatabase)):
        p = positionDatabase[i]
        if p.ratherRapid and p.playerFinal > p.bestFinal:
            feedback[i] = AC.RAPID # rather rapid
        elif p.playerNNB <= p.bestNNB - 40:
            feedback[i] = AC.BLUNDER
        elif p.playerFinal <= p.bestFinal - 30:
            feedback[i] = AC.MISTAKE
        elif p.playerNNB <= p.bestNNB - 7 or p.playerFinal <= p.bestFinal - 20:
            feedback[i] = AC.INACCURACY

        
        if p.playerFinal >= p.bestFinal - 10 or (p.playerFinal >= p.bestFinal - 15 and p.playerNNB >= p.bestNNB - 5):
            feedback[i] = AC.EXCELLENT
        elif p.playerFinal >= p.bestFinal - 5:
            feedback[i] = AC.BEST
            
        
            
            

    smallSize = 70
    bigResolution = 4
    width = 1300

    # Graph only accepts a minimum of 4 positions, otherwise interpolation doesn't work
    showGraphs = (len(levels) >= 4)
    if showGraphs:
        smallGraph = EvalGraph.Graph(True, evals, levels, feedback, 950, 970, width, 200, 1, smallSize, bigRes = bigResolution)
        bigWidth = width if len(levels) >= 200 else (width // 2) # Cut the big graph in half if there are under 200 positions
        showBig = len(levels) >= 50 # If there are under 50 positions, don't show the big graph at all
        if showBig:
            bigGraph = EvalGraph.Graph(False, evals, levels, feedback, 950, 1220, bigWidth, 200, bigResolution, smallSize)
    greysurface = pygame.Surface([width, 200])
    greysurface.blit(images[STRIPES],[0,0])
    

    wasPressed = False

    updatePosIndex = None

    while True:

        # --- [ CALCULATIONS ] ---

        # Mouse position
        mx,my = c.getScaledPos(*pygame.mouse.get_pos())
        pressed = pygame.mouse.get_pressed()[0]
        click = not pressed and wasPressed
        startPressed = pressed and not wasPressed
        wasPressed = pressed


        # Update with mouse event information        
        buttons.updatePressed(mx, my, click)
        analysisBoard.update(mx, my, click)
        
        c.realscreen.fill(MID_GREY)
        c.screen.fill(MID_GREY)

        # Hypothetical buttons
        if buttons.get(B_HYP_LEFT).clicked and analysisBoard.hasHypoLeft():
            analysisBoard.hypoLeft()
        elif buttons.get(B_HYP_RIGHT).clicked and analysisBoard.hasHypoRight():
            analysisBoard.hypoRight()
        elif buttons.get(B_HYP_MAXLEFT).clicked:
            while analysisBoard.hasHypoLeft():
                analysisBoard.hypoLeft()
        elif buttons.get(B_HYP_MAXRIGHT).clicked:
            while analysisBoard.hasHypoRight():
                analysisBoard.hypoRight()

        # Left/Right Buttons
        if buttons.get(B_LEFT).clicked and analysisBoard.positionNum > 0:
            analysisBoard.updatePosition(analysisBoard.positionNum-1)
            positionNum -= 1
            print(analysisBoard.position.url)
            
        elif buttons.get(B_RIGHT).clicked and analysisBoard.positionNum < len(positionDatabase) - 1:
            analysisBoard.updatePosition(analysisBoard.positionNum+1)
            positionNum += 1
            print(analysisBoard.position.url)


        # Update Graphs
        if showGraphs:
            o = smallGraph.update(positionNum, mx,my, pressed, startPressed, click)
            if o != None:
                positionNum = o
                analysisBoard.updatePosition(positionNum)
            if showBig:
                o = bigGraph.update(positionNum, mx, my, pressed, startPressed, click)
                if o != None:
                    positionNum = o
                    analysisBoard.updatePosition(positionNum)
        
        
            
        buttons.get(B_LEFT).isAlt = analysisBoard.positionNum == 0
        buttons.get(B_RIGHT).isAlt = analysisBoard.positionNum == len(positionDatabase) - 1

        buttons.get(B_HYP_LEFT).isAlt = not analysisBoard.hasHypoLeft()
        buttons.get(B_HYP_MAXLEFT).isAlt = not analysisBoard.hasHypoLeft()
        buttons.get(B_HYP_RIGHT).isAlt = not analysisBoard.hasHypoRight()
        buttons.get(B_HYP_MAXRIGHT).isAlt = not analysisBoard.hasHypoRight()

        currPos = analysisBoard.position
        feedbackColor = AC.feedbackColors[feedback[positionNum]]
        evalBar.tick(currPos.evaluation, feedbackColor)


        # --- [ DISPLAY ] ---

        # Now that we're about to display things, reset hitbox data so that new graphics components can be appended
        #HT.log()
        #print(HT.at(mx,my),mx,my)
        HT.reset()

        # Buttons
        buttons.display(c.screen)
        
        # Tetris board
        analysisBoard.draw()

        # Evaluation Graph
        c.screen.blit(greysurface, [950, 970])
        c.screen.blit(greysurface, [950, 1220])
        if showGraphs:
            smallGraph.display(mx,my, positionNum)
            if showBig:
                bigGraph.display(mx, my, positionNum)
        

        # Eval bar
        HT.blit("eval", evalBar.drawEval(), [20,20])

        # Text for level / lines / score
        c.screen.blit(c.fontbig.render("Level: {}".format(analysisBoard.position.level), True, BLACK), [1300, 20])
        c.screen.blit(c.fontbig.render("Lines: {}".format(analysisBoard.position.lines), True, BLACK), [1300, 120])
        c.screen.blit(c.fontbig.render("Score: {}".format(analysisBoard.position.score), True, BLACK), [1300, 220])
        c.screen.blit(c.fontbig.render("playerNNB: {}".format(analysisBoard.position.playerNNB), True, BLACK), [1300, 360])
        c.screen.blit(c.fontbig.render("bestNNB: {}".format(analysisBoard.position.bestNNB), True, BLACK), [1300, 460])
        c.screen.blit(c.fontbig.render("playerFinal: {}".format(analysisBoard.position.playerFinal), True, BLACK), [1300, 560])
        c.screen.blit(c.fontbig.render("bestFinal: {}".format(analysisBoard.position.bestFinal), True, BLACK), [1300, 660])
        c.screen.blit(c.fontbig.render("RatherRapid: {}".format(analysisBoard.position.ratherRapid), True, BLACK), [1300, 760])
        c.screen.blit(c.fontbig.render("{} Hz Analysis".format(hzInt), True, BLACK), [1900, 120])
        c.screen.blit(c.fontbig.render(AC.feedbackString[feedback[positionNum]], True, feedbackColor), [1900, 220])

        # Text for position number
        text = c.fontbig.render("Position: {}".format(analysisBoard.positionNum + 1), True, BLACK)
        c.screen.blit(text, [1300,900])

        # Draw timestamp
        frameNum = analysisBoard.positionDatabase[analysisBoard.positionNum].frame
        if frameNum != None:
            text = c.fontbig.render(c.timestamp(frameNum), True, BLACK)
            c.screen.blit(text, [1000,600] )

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.display.quit()
                sys.exit()
                return True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    analysisBoard.toggle()
                
            elif event.type == pygame.VIDEORESIZE:

                c.realscreen = pygame.display.set_mode(event.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            
        c.handleWindowResize()
        pygame.display.update()
