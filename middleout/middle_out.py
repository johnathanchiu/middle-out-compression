# Middle-Out Compression Algorithm
# © Johnathan Chiu, 2019

from middleout.utils import *
from middleout.huffman import *

from multiprocessing import Pool
from tqdm import tqdm


class MiddleOutUtils:
    """ Utils Class for MiddleOut """

    @staticmethod
    def partition_compressed_bits(bit_stream, size):
        pointer, back_transform, total = 0, 0, 0
        max_bits = MiddleOut.BIT_DEPTH

        while total < size:
            if bit_stream[0] == '1':
                bit_stream = bit_stream[1:]
                total += 1; back_transform += 1; pointer += 1
            else:
                if bit_stream[:2] == '01':
                    pointer += max_bits + 2; copy_size = unary_to_int(bit_stream[pointer:]) + 3
                    pointer += copy_size - 3 + 1; total += copy_size
                elif bit_stream[:4] == '0010':
                    pointer += 4; copy_size = unary_to_int(bit_stream[pointer:]) + 3
                    pointer += copy_size - 3 + 1; total += copy_size
                elif bit_stream[:4] == '0011':
                    pointer += 3; copy_size = unary_to_int(bit_stream[pointer:]) + 3
                    pointer += copy_size - 3 + 1; total += copy_size
                elif bit_stream[:5] == '00010':
                    pointer += 5; copy_size = unary_to_int(bit_stream[pointer:]) + 3
                    pointer += copy_size - 3 + 1; total += copy_size
                else:
                    pointer += 5 + max_bits; copy_size = unary_to_int(bit_stream[pointer:]) + 3
                    pointer += copy_size - 3 + 1; total += copy_size
        return bit_stream[:pointer], bit_stream[pointer:], back_transform


class MiddleOutCompressor:
    """ Compressor Class """

    @staticmethod
    def byte_compression(uncompressed):
        compressed_stream = ''
        if len(uncompressed) == 0:
            return compressed_stream
        preceding, match, right = {}, [], []
        literal_count, pointer, match_start = 0, 0, 0
        prev_one, prev_two = None, None
        while pointer < len(uncompressed):
            match = uncompressed[pointer:pointer+2]
            match_start = pointer

            if MiddleOut.DEBUG:
                print("pointer:", pointer, "match:", match)
                print("match start:", match_start)
                print("compressed:", compressed_stream)
                frmt = "{:>3}"*len(uncompressed)
                print(frmt.format(*list(range(0, len(uncompressed)))))
                print(frmt.format(*uncompressed))

            while (tuple(match) in preceding and match_start - len(match) >= preceding[tuple(match)]) or \
                    (match.count(match[0]) == len(match) and len(match) >= 2):
                if len(match) == 2:
                    pointer += 1
                pointer += 1
                if pointer >= len(uncompressed):
                    if match.count(match[0]) == len(match):
                        back_reference = unsigned_binary(match_start, bits=MiddleOut.BIT_DEPTH)
                        reference_size = unsigned_binary(len(match) - 1, bits=MiddleOut.BIT_DEPTH)
                        compressed_stream += '00011' + back_reference + reference_size; match = []
                    else:
                        if tuple(match) in preceding:
                            reference_size, match_begin = unsigned_unary(len(match) - 3), preceding[tuple(match)]
                            if match_begin == prev_one:
                                compressed_stream += '00010' + reference_size
                            elif match_begin == prev_two:
                                compressed_stream += '0010' + reference_size
                            else:
                                back_reference = unsigned_binary(match_begin, bits=MiddleOut.BIT_DEPTH)
                                compressed_stream += '01' + back_reference + reference_size; match = []
                            prev_one, prev_two = match_begin, prev_one
                    break
                match.append(uncompressed[pointer])

            if len(match) > 3:
                match = match[:-1]
                if match.count(match[0]) == len(match):
                    back_reference = unsigned_binary(match_start, bits=MiddleOut.BIT_DEPTH)
                    reference_size = unsigned_binary(len(match) - 1, bits=MiddleOut.BIT_DEPTH)
                    compressed_stream += '00011' + back_reference + reference_size
                else:
                    if tuple(match) in preceding:
                        reference_size, match_begin = unsigned_unary(len(match) - 3), preceding[tuple(match)]
                        if match_begin == prev_one:
                            compressed_stream += '00010' + reference_size
                        elif match_begin == prev_two:
                            compressed_stream += '0010' + reference_size
                        else:
                            back_reference = unsigned_binary(match_begin, bits=MiddleOut.BIT_DEPTH)
                            compressed_stream += '01' + back_reference + reference_size
                        prev_one, prev_two = match_begin, prev_one
                pointer -= 1

            else:
                if len(match) >= 1:
                    if prev_one is not None and match[0] == uncompressed[prev_one]:
                        compressed_stream += '0011'
                    else:
                        literal_count += 1
                        compressed_stream += '1'; right.append(match[0])
                if len(match) > 2:
                    pointer -= 1

            if pointer <= len(uncompressed) - MiddleOut.MAX_DISTANCE:
                forward_values = uncompressed[pointer:pointer+MiddleOut.MAX_DISTANCE]
                for j in range(2, len(forward_values) + 1):
                    if tuple(forward_values[:j]) not in preceding:
                        preceding[tuple(forward_values[:j])] = pointer
            pointer += 1

        if literal_count > len(uncompressed) * 0.75:
            return '1' + unsigned_bin_list(uncompressed)
        return '0' + compressed_stream + MiddleOutCompressor.byte_compression(right)


class MiddleOutDecompressor:
    """ Decompressor Class """

    @staticmethod
    def merge_bytes(bit_stream, right):
        uncompressed, right_pointer = [], 0
        prev_one, prev_two = None, None

        while len(bit_stream) > 0:
            if bit_stream[0] == '1':
                bit_stream = bit_stream[1:]
                uncompressed.append(right[right_pointer])
                right_pointer += 1
            else:
                if bit_stream[:2] == '01':
                    bit_stream = bit_stream[2:]; back_ref = unsigned_int(bit_stream[:MiddleOut.BIT_DEPTH])
                    bit_stream = bit_stream[MiddleOut.BIT_DEPTH:]; copy_size = unary_to_int(bit_stream) + 3
                    bit_stream = bit_stream[copy_size - 3 + 1:]
                    [uncompressed.append(uncompressed[i+back_ref]) for i in range(copy_size)]
                    prev_one, prev_two = back_ref, prev_one
                elif bit_stream[:4] == '0010':
                    bit_stream = bit_stream[4:]; copy_size = unary_to_int(bit_stream) + 3
                    bit_stream = bit_stream[copy_size - 3 + 1]
                    [uncompressed.append(uncompressed[i+prev_two]) for i in range(copy_size)]
                    prev_one, prev_two = prev_two, prev_one
                elif bit_stream[:4] == '0011':
                    bit_stream = bit_stream[4:]
                    uncompressed.append(uncompressed[prev_one])
                elif bit_stream[:5] == '00010':
                    bit_stream = bit_stream[4:]; copy_size = unary_to_int(bit_stream) + 3
                    bit_stream = bit_stream[copy_size - 3 + 1]
                    [uncompressed.append(uncompressed[i+prev_one]) for i in range(copy_size)]
                    prev_one, prev_two = prev_one, prev_one
                else:
                    bit_stream = bit_stream[5:]; back_ref = unsigned_int(bit_stream[:MiddleOut.BIT_DEPTH])
                    bit_stream = bit_stream[MiddleOut.BIT_DEPTH:]
                    copy_size = unsigned_int(bit_stream[:MiddleOut.BIT_DEPTH])
                    bit_stream = bit_stream[MiddleOut.BIT_DEPTH:]
                    [uncompressed.append(uncompressed[back_ref+i]) for i in range(copy_size)]
        return uncompressed


    @staticmethod
    def bit_decompress(compressed, length):
        if length == 0: return [], ''
        iden, compressed = compressed[0], compressed[1:]

        if iden == '1':
            return unsigned_int_list(compressed[:length*8]), compressed[length*8:]
        partition, compressed, back_transform = MiddleOutUtils.partition_compressed_bits(compressed, length)
        right, compressed = MiddleOutDecompressor.bit_decompress(compressed, back_transform)
        return MiddleOutDecompressor.merge_bytes(partition, right), compressed


class MiddleOut:
    """ Passes values into the compressor and decompressor, pads streams """

    BIT_DEPTH, STRIDE = 8, 256
    MAX_DISTANCE = 9
    DEBUG = False

    @staticmethod
    def middle_out_compress(partitions):
        with Pool(8) as p:
            compression = p.map(MiddleOutCompressor.byte_compression, partitions)
        return ''.join(compression)

    @staticmethod
    def middle_out_decompress(bit_stream, bytes_count, visualizer=True):
        byte_chunks = []
        partitions, remainder = bytes_count // MiddleOut.STRIDE, bytes_count % MiddleOut.STRIDE
        if visualizer:
            parts = tqdm(range(partitions + 1), desc='running middle-out decompression scheme')
        else:
            parts = range(partitions + 1)
        for c in parts:
            if c == partitions:
                decompressed, bit_stream = MiddleOutDecompressor.bit_decompress(bit_stream, remainder)
                byte_chunks.append(decompressed)
            else:
                decompressed, bit_stream = MiddleOutDecompressor.bit_decompress(bit_stream, MiddleOut.STRIDE)
                byte_chunks.append(decompressed)
        return (lambda l: [item for sublist in l for item in sublist])(byte_chunks)

    @staticmethod
    def compress(byte_stream, stride=256, distance=9, visualizer=True):
        assert stride >= 256 and stride % 256 == 0, "invalid back reference size"
        try:
            assert (2 ** minimum_bits(distance - 2)) - 1 == distance - 2
        except AssertionError:
            dist = distance
            while (2 ** minimum_bits(dist)) - 1 > distance - 2:
                distance += 1

        partitions = split_file(byte_stream, chunksize=stride)

        if visualizer:
            parts = tqdm(partitions, desc='running middle-out compression scheme')
        else:
            parts = partitions

        MiddleOut.STRIDE = stride
        MiddleOut.BIT_DEPTH, MiddleOut.MAX_DISTANCE = minimum_bits(stride - 1), distance

        mo, minbits = MiddleOut.middle_out_compress(parts), minimum_bits(len(byte_stream))

        stride_bits = unsigned_unary(stride // 256)
        header = unsigned_unary(minbits) + unsigned_binary(len(byte_stream), bits=minbits) + stride_bits

        compressed = header + mo; pad = pad_stream(len(compressed)); num_padded = signed_bin(pad, bits=4)
        mo_compressed = compressed + ('0' * pad) + num_padded

        return unsigned_int_list(mo_compressed)

    @staticmethod
    def decompress(compressed_bits, visualizer=True):

        compressed_bits = remove_padding(compressed_bits)

        bit_count_length = unary_to_int(compressed_bits)
        compressed_bits = compressed_bits[bit_count_length+1:]
        length, compressed_bits = unsigned_int(compressed_bits[:bit_count_length]), compressed_bits[bit_count_length:]
        stride_size = unary_to_int(compressed_bits) * 256; compressed_bits = compressed_bits[int(stride_size//256)+1:]
        compressed_bits = compressed_bits[8:]

        MiddleOut.STRIDE, MiddleOut.BIT_DEPTH = stride_size, minimum_bits(stride_size - 1)

        return MiddleOut.middle_out_decompress(compressed_bits, length, visualizer=visualizer)
