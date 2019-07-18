import array
import os


def positive_binary(num, bits=8):
    length = '{0:0' + str(bits) + 'b}'
    return length.format(num)


def positive_int(binary):
    return int(binary, 2)


def positiveInt_list(binary, bits=8):
    return [int(binary[i:i+bits], 2) for i in range(0, len(binary), bits)]


def positiveBin_list(vals, bits=8):
    length = '{0:0' + str(bits) + 'b}'
    return ''.join([length.format(i) for i in vals])


def convertBin(num, bits=8):
    s = bin(num & int("1" * bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)


def convertInt(binary, bits=8):
    binary = int(binary, 2)
    """compute the 2's complement of int value val"""
    if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        binary = binary - (1 << bits)  # compute negative value
    return binary  # return positive value as is


def convertBin_list(intList, bits=8):
    def bindigits(val, bits=8):
        s = bin(val & int("1" * bits, 2))[2:]
        return ("{0:0>%s}" % (bits)).format(s)
    binary = ''
    for x in intList:
        binary += bindigits(x, bits=bits)
    return binary


def convertInt_list(binary, bits=8):
    def two_complement(binary, bits=8):
        binary = int(binary, 2)
        """compute the 2's complement of int value val"""
        if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            binary = binary - (1 << bits)  # compute negative value
        return binary  # return positive value as is
    intList = []
    for x in range(0, len(binary), bits):
        intList.append(two_complement(binary[x:x+bits], bits=bits))
    return intList


def unaryconverter(num):
    unary = ''
    for _ in range(num):
        unary += '1'
    unary += '0'
    return unary


def unaryToInt(unr):
    num = 0
    while unr[num] != '0':
        num += 1
    return num


def minimum_bits(num):
    if num == 0:
        return 1
    return num.bit_length()


def pad_stream(length):
    padding = 4 - (length % 8)
    if padding >= 0:
        return padding
    return 8 + padding


def remove_padding(stream):
    num_pad_bits = stream[-4:]
    stream = stream[:-4]
    num_pad = -1 * convertInt(num_pad_bits, bits=4)
    return stream[:num_pad]


def writeFile(bitstring, fileName=None):
    bit_strings = [bitstring[i:i + 8] for i in range(0, len(bitstring), 8)]
    byte_list = [int(b, 2) for b in bit_strings]
    filename = fileName + '.bin'
    with open(filename, 'wb') as f:
        f.write(bytearray(byte_list))


def writeFileBytes(bytes_list, fileName=None):
    with open(fileName, 'wb') as f:
        f.write(bytearray(bytes_list))


def readFile(fileName):
    size = os.stat(fileName).st_size
    with open(fileName, 'rb') as f:
        bytes = f.read(int(size))
    bit_string = [convertBin(b, bits=8) for b in bytes]
    bits = ''.join(bit_string)
    return bits


def readFileBytes(fileName, partial=0):
    assert partial <= 1, "partial percentage greater than 100%"
    size = os.stat(fileName).st_size
    if partial:
        size *= partial
    with open(fileName, 'rb') as f:
        bytes = f.read(int(size))
    return array.array('B', list(bytes))


def split_file(file_values, chunksize=32000):
    return [array.array('B', file_values[x:x+chunksize]) for x in range(0, len(file_values), chunksize)]


def size_of_file(filename):
    return os.stat(filename).st_size

