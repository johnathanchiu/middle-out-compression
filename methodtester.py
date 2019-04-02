from middleOut.MiddleOut import *

import collections

x = '0000100111110000000011001111111011111010000000010000000111111000000110100000010000001000111110001111111111111111' \
    '11111110000000010000111100001001000000'
x = '00000000010100100101100011111111110000000000'
layer_one, uncomp_part = MiddleOut.layer_one_compression(x)
print(layer_one)
# layer_one = [0, 10000, 0, 11010, 0, 10011]
# uncomp_part = ['1', '100110', '000101010']
print(uncomp_part)
lib = MiddleOut.build_library(uncomp_part)
print(lib)
layer_two, unc = MiddleOut.layer_two_compression(uncomp_part, lib)
print("layer2", layer_two)
print(unc)
lib2 = MiddleOut.build_library(unc, size=4)
layer_three = MiddleOut.layer_three_compression(unc, lib2)
print("layer:", layer_three)
y = MiddleOut.merge_compressed(layer_one, layer_two, layer_three)
lib += lib2 + y
y = lib
print(y)
z = MiddleOut.decompressStream(y)
print(z)
print(x)
print(z == x)
