board1 = "00000000000000000000000000000000000000000000000000000000000000000000000100110000010011000011101101001111111110111111111011111111101111111110111111111011111111101111111110111111111011111111101111111110"
board2 = "00000000000000000000000000000000000000000000000000000000000011000000001100110000110011000011101101001111111110111111111011111111101111111110111111111011111111101111111110111111111011111111101111111110"
import numpy as np
b1 = [0 if s == "0" else 1 for s in board1]
b2 = [0 if s == "0" else 1 for s in board2]
b1 = np.reshape(b1,(20,10))
b2 = np.reshape(b2,(20,10))
print(b1)
print(b2)
print(b1+2*b2)
