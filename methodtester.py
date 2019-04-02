from middleOut.MiddleOut import *

import collections

x = '1000000100110111111110001010101000000000'
layer_one, uncomp_part = MiddleOut.layer_one_compression(x)
# layer_one = [0, 10000, 0, 11010, 0, 10011]
# uncomp_part = ['1', '100110', '000101010']
print(layer_one)
print(uncomp_part)
lib = MiddleOut.build_library(uncomp_part)
print(lib)
layer_two, unc = MiddleOut.layer_two_compression(uncomp_part, lib)
print(layer_two)
print(unc)
lib2 = MiddleOut.build_library(unc, size=4)
print(lib2)
layer_three = MiddleOut.layer_three_compression(unc, lib2)
print(layer_three)
y = MiddleOut.merge_compressed(layer_one, layer_two, layer_three)
lib += lib2 + y
y = lib
print(y)
z = MiddleOut.decompressStream(y)
print(z)
print(x)
print(z == x)
