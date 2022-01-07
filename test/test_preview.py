"""
This file tests the auto-optimization code inside blockmatch.py.
This is for finding the four minos within a given preview box.
"""

import pytest
import cv2
import time
import glob
from calibrate.blockmatch import find_piece, draw_and_show, convert_to_grayscale, BLOCKMATCH_SCALE_FACTOR


# run using:
# python -m pytest -s
def test_previews():
    t = time.time()
    for imagePath in glob.glob("test/image/preview/*.png"):
        print(f"testing {imagePath}")
        # load the image, convert it to grayscale, and initialize the
        # bookkeeping variable to keep track of the matched region
        image = cv2.imread(imagePath, 0)
        dims = list(image.shape)
        # swap xy lol, opencv ftw
        dims[1], dims[0] = (
            int(dims[0] * (BLOCKMATCH_SCALE_FACTOR / 2.0)),
            int(dims[1] * (BLOCKMATCH_SCALE_FACTOR / 2.0)),
        )

        image = cv2.resize(image, dims)
        result = find_piece(image)
        image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        draw_and_show(image_color, result)
    print("Time:", time.time() - t)
