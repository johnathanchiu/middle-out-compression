from middleOut.utils import *
from middleOut.MiddleOut import MiddleOut
from middleOut.EntropyReduction import EntropyReduction

from collections import Counter
import imageio

# file = '/Users/johnathanchiu/Documents/CompressionPics/tests/IMG_0104.jpg'
# values = [b - 128 for b in readFileBytes(file)]
values = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 2, 1, 1, 2, 2, 2]
result = MiddleOut.middle_out(values, size=2)

size = len(result) // 8
print(size)
print(len(values))
# print(size_of_file(file))
# print(size / size_of_file(file))
