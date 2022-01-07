"""
This file tests the auto-optimization code inside blockmatch.py.
This is for finding the four minos within a given preview box.

run using:
python -m pytest -s
"""

import pytest
import cv2
import time
import glob
from calibrate.blockmatch import find_piece, draw_and_show_multi, BLOCKMATCH_SCALE_FACTOR, BLOCK_SIZE_PX
from calibrate.rect import Rect
ROOT = "test/image/preview/"

def single_preview(image_name, reference_result):
    imagePath = ROOT + image_name
    print(imagePath)
    image = cv2.imread(imagePath, 0)
    dims = list(image.shape)
    # swap xy lol, opencv ftw
    dims[1], dims[0] = (
        int(dims[0] * (BLOCKMATCH_SCALE_FACTOR / 2.0)),
        int(dims[1] * (BLOCKMATCH_SCALE_FACTOR / 2.0)),
    )

    image = cv2.resize(image, dims)
    result = find_piece(image)
    # we must be within 2 nes px of intended result.
    
    #if reference_result.close_to(result, BLOCK_SIZE_PX / 2, BLOCK_SIZE_PX / 2):
    #    return
    #uh oh, we failed
    image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    wrong = (result, (0,0,255))
    correct = (reference_result, (0,255,0))
    draw_and_show_multi(image_color, [wrong, correct])
    print (result, reference_result)
    assert reference_result == result

def test_emu():
    single_preview("test1.png", Rect(4, 151, 280, 286))

def test_harry1():
    single_preview("test4.png", Rect(-1, 147, 283, 283))

def test_harry2():
    single_preview("test5.png", Rect(13, 151, 275, 281))

def test_harry3():
    single_preview("test6.png", Rect(9, 152, 278, 279))

def test_harry4():
    single_preview("test7.png", Rect(1, 147, 285, 286))

def test_harry5():
    single_preview("test8.png", Rect(4, 158, 279, 270))

def test_harry6():
    single_preview("test9.png", Rect(-2, 144, 265, 276))