import numpy as np
from PieceMasks import *
import math
import time
import cProfile
import os


from TetrisUtility import *
from Callibration import callibrate
from RenderVideo import render
from Analysis import analyze

import config as c

import easygui

        
testing = False
def main():

    if testing:

        testboard = np.array([
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                  [1, 0, 0, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 1, 1, 1, 0, 0, 0,],
                  [1, 1, 1, 1, 1, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 1, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0,],
                  [1, 1, 1, 1, 0, 0, 0, 0, 1, 1,],
                  [1, 1, 1, 1, 1, 0, 0, 0, 1, 1,],
                  [1, 1, 1, 1, 0, 1, 1, 1, 1, 1,]
                  ])
        testplacement = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 1, 1, 0, 0,],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
        ])
        testplacement2 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
        ])

        from Position import Position
        
        positionDatabase = [Position(testboard, S_PIECE, S_PIECE, placement = testplacement, evaluation = 0.2)]
        positionDatabase.append(Position(testboard+testplacement, I_PIECE, L_PIECE, placement = testplacement2, evaluation = 0.7))

    else:
        while True:
            c.filename = input("Enter a full filepath for the video: ").strip()
            if os.path.isfile(c.filename):
                break
            else:
                print("Invalid filepath.")
                
        print(c.filename)
        output = callibrate()
        
        if output == None:
            return # exit if pygame screen closed
        
        firstFrame, lastFrame, bounds, nextBounds = output
        print(bounds.x1,bounds.y1,bounds.x2,bounds.y2)
        print(nextBounds.x1,nextBounds.y1,nextBounds.x2,nextBounds.y2)
        print(firstFrame, lastFrame)

        print("Successfully callibrated video.")
        
        
        positionDatabase = render(firstFrame, lastFrame, bounds, nextBounds)
        print("Num positions: ", len(positionDatabase))
        
        

    if positionDatabase != None:
        analyze(positionDatabase)

if __name__ == "__main__":
    main()
