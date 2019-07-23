from MiddleOut.utils import *
from MiddleOut.MiddleOut import MiddleOut
from MiddleOut.EntropyEncoder import *

import random
import time

start_time = time.time()

file = '/Users/johnathanchiu/Documents/CompressionPics/tests/IMG_1072.jpg'
values = readFileBytes(file)
result = MiddleOut.middle_out(values, size=2)

size = len(result) // 8
print(size)
print(size_of_file(file))
print(size / size_of_file(file))
