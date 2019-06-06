from middleOut.utils import convertBin_list, convertInt, convertBin, \
    convertInt_list, unaryconverter, unaryToInt, positive_binary, positive_int, \
    minimum_bits

test_bit = positive_binary(8, bits=8)
back = positive_int(test_bit)
print(test_bit, back)


num = 1
minbit = minimum_bits(num)
print("minimum bits:", minbit)
print(unaryconverter(minbit))
bitconv = positive_binary(num, bits=minbit)[1:]
print(bitconv)
bitconv = '1' + bitconv
print(positive_int(bitconv))

