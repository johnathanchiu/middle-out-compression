# Middle-Out Compression Algorithm
# © Johnathan Chiu, 2019

from collections import Counter
from middleout.utils import *
from middleout.runlength import rld, rle, rlepredict


class MiddleOutUtils:

    @staticmethod
    def max_key(d):
        v = list(d.values())
        return list(d.keys())[v.index(max(v))]

    @staticmethod
    def build_library(byte_stream):
        count = 0
        dictionary = {}
        while count <= len(byte_stream) - MiddleOutCompressor.LIBRARY_SIZE:
            partition = tuple(byte_stream[count:count + MiddleOutCompressor.LIBRARY_SIZE])
            if partition not in dictionary:
                dictionary[partition] = 1
            else:
                dictionary[partition] += 1
            count += 1
        large_occur = MiddleOutUtils.max_key(dictionary)
        ratio = dictionary[large_occur] / len(byte_stream)
        MiddleOutCompressor.LIBRARY = large_occur
        return large_occur, ratio

    @staticmethod
    def merge_split(splits, left, right, debug=False):
        if debug: print("merging", splits, left, right)
        values = []
        left_count, right_count = 0, 0
        for i in splits:
            if i == '0':
                values.append(left[left_count]); left_count += 1
            else:
                values.append(right[right_count]); right_count += 1
        return values

    @staticmethod
    def count_split(values):
        l_c, r_c = 0, 0
        for i in values:
            if i == '1': r_c += 1
            else: l_c += 1
        return l_c, r_c

    @staticmethod
    def grab_count(values, total, start_z=False):
        count = 0 if start_z else MiddleOutCompressor.LIBRARY_SIZE*8
        ent, remaining = 0, 0
        while ent < total:
            if values[count] == '0':
                ent += MiddleOutCompressor.LIBRARY_SIZE; count += 1
            else:
                ent += 1; count += 1; remaining += 1
        return count, remaining

    @staticmethod
    def splitter(values):
        counter, split_set, occurrence_count = 0, set([]), Counter(values)
        occurrence, large = len(occurrence_count), MiddleOutUtils.max_key(occurrence_count)
        occ_copy, largest = occurrence_count.copy(), large
        split = False
        if occurrence == 1:
            return '', values, [], '0', '1', '0'
        while counter / len(values) < MiddleOutCompressor.SPLIT:
            large = MiddleOutUtils.max_key(occurrence_count)
            split_set.add(large)
            counter += occurrence_count[large]
            occurrence_count[large] = 0
        if occ_copy[largest] / len(values) >= MiddleOutCompressor.FORCE_SPLIT or len(split_set) <= 3:
            split = True
        if not split:
            if len(values) < MiddleOutCompressor.LIBRARY_SIZE or \
                    occ_copy[largest] < len(values) / occurrence:
                return None, None, None, None, None, '1'
            if 0 < MiddleOutCompressor.LIBRARY_SIZE and MiddleOutCompressor.HIGHER_COMPRESSION:
                _, ratio = MiddleOutUtils.build_library(values)
                if ratio >= MiddleOutCompressor.MINIMUM_LIB_RATIO:
                    return '', values, [], '0', '0', '0'
        return MiddleOutUtils.branch_tree(values, split_set)

    @staticmethod
    def branch_tree(values, left_tree):
        split = ''
        right, left = array.array('B', []), array.array('B', [])
        for v in values:
            if v in left_tree: split += '0'; left.append(v)
            else: split += '1'; right.append(v)
        return split, left, right, '1', '0', '0'


class MiddleOutDecompressor:

    @staticmethod
    def decompress(stream, length, debug=False):
        if debug: print("length: ", length)
        uncompressed = []
        if len(stream) == 0 or length == 0:
            return uncompressed, stream
        literal, stream = stream[0], stream[1:]
        if literal == '1':
            return positiveInt_list(stream[:length*8]), stream[length*8:]
        rl, stream, r_c = stream[0], stream[1:], None
        if rl == '1':
            minbits = unaryToInt(stream); stream = stream[minbits+1:]
            r_c = positive_int(stream[:minbits]) + 1
            stream = stream[minbits:]
        split, entropy, stream = stream[0], stream[1], stream[2:]
        if debug: print("split:", split == '1', ", entropy: ", entropy == '1', ", run length: ", rl == '1')
        if split == '1':
            return MiddleOutDecompressor.decompress_split_helper(stream, length, rl, r_c, debug=debug)
        else:
            if entropy == '1':
                return MiddleOutDecompressor.decompress_entropy_helper(stream, debug=debug)
            else:
                library = positiveInt_list(stream[:8*MiddleOutCompressor.LIBRARY_SIZE])
                partition_size, remaining = MiddleOutUtils.grab_count(stream, length)
                partition, stream = stream[:partition_size], stream[partition_size:]
                if debug:
                    print("partition size: ", partition_size, "remaining: ", remaining)
                    print("library:", library)
                remain, stream = MiddleOutDecompressor.decompress(stream, remaining, debug=debug)
                return MiddleOutDecompressor.decompress_helper(partition, library, remain, debug=debug), stream

    @staticmethod
    def decompress_split_helper(stream, length, rl_iden, rl_c, debug=False):
        back_transform, stream = stream[:length], stream[length:]
        if debug: print("shift: ", back_transform)
        left_count, right_count = MiddleOutUtils.count_split(back_transform)
        if debug: print("left_count: ", left_count, ", right_count: ", right_count)
        left, stream = MiddleOutDecompressor.decompress(stream, left_count, debug=debug)
        if rl_iden == '1':
            right, stream = MiddleOutDecompressor.decompress(stream, rl_c, debug=debug)
            right = rld(right)
        else:
            right, stream = MiddleOutDecompressor.decompress(stream, right_count, debug=debug)
        if debug: print("left: ", left); print("right: ", right)
        return MiddleOutUtils.merge_split(back_transform, left, right), stream

    @staticmethod
    def decompress_entropy_helper(stream, debug=False):
        library, stream = stream[:8], stream[8:]
        if debug: print("library: ", library)
        minbits = unaryToInt(stream); stream = stream[minbits+1:]
        num = positive_int(stream[:minbits]) + 1; stream = stream[minbits:]
        uncompressed = [positive_int(library)] * num
        return uncompressed, stream

    @staticmethod
    def decompress_helper(partition, lib, remaining, debug=False):
        partition = partition[8*MiddleOutCompressor.LIBRARY_SIZE:]
        if debug: print("part: ", partition, ", lib: ", lib)
        uncompressed, remaining_count = [], 0
        for i in partition:
            if i == '1':
                uncompressed.append(remaining[remaining_count])
                remaining_count += 1
            else:
                for x in range(MiddleOutCompressor.LIBRARY_SIZE):
                    uncompressed.append(lib[x])
        if debug: print("uncompressed: ", uncompressed)
        return uncompressed


class MiddleOutCompressor:

    LIBRARY_SIZE = 0
    SPLIT = 0.50
    RUNLENGTH_CUTOFF = 0.4
    MINIMUM_LIB_RATIO = 0.10
    FORCE_SPLIT = 0.3
    LIBRARY = None
    HIGHER_COMPRESSION = True

    @staticmethod
    def byte_compression(values, run=False, debug=False):
        if len(values) == 0: return ''
        if debug: print("original values: ", values); print("remaining length: ", len(values))
        if run:
            return '1' + positiveBin_list(values, bits=8)
        back_transform, left, right, split, entrop, lit = MiddleOutUtils.splitter(values)
        if lit == '1':
            return '1' + positiveBin_list(values, bits=8)
        if debug: print("split:", split == '1', ", entropy:", entrop == '1')
        lib, comp_l = '', ''
        if split == '0':
            if entrop == '1':
                lib, minbits = positive_binary(left[0], bits=8), minimum_bits(len(left) - 1)
                comp_l, left = unaryconverter(minbits) + positive_binary(len(left) - 1, bits=minbits), []
                if debug: print("library:", positiveInt_list(lib))
            else:
                l_ = MiddleOutCompressor.LIBRARY
                lib = positiveBin_list(l_, bits=8)
                comp_l, left = MiddleOutCompressor.middle_out_helper(left, l_, debug=debug)
        right_size, rl, r_encode = rlepredict(right), '0', ''
        rlpred = False
        if len(right) > 0 and right_size < int(len(right) * MiddleOutCompressor.RUNLENGTH_CUTOFF):
            right, rl, minbits = rle(right), '1', minimum_bits(right_size - 1)
            r_encode = unaryconverter(minbits) + positive_binary(right_size - 1, bits=minbits)
            rlpred = True
        header = lit + rl + r_encode + split + entrop + back_transform + lib + comp_l
        if debug: print("header:", header)
        return header + MiddleOutCompressor.byte_compression(left, debug=debug) + \
               MiddleOutCompressor.byte_compression(right, run=rlpred, debug=debug)

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, debug=False):
        if debug: print("library: ", compression_dict)
        count, unc_count = 0, 0
        compressed = ''; uncompressed = []
        while count < len(byte_stream):
            tup = tuple(byte_stream[count:count+MiddleOutCompressor.LIBRARY_SIZE])
            if tup == compression_dict:
                compressed += '0'; count += len(tup)
            else:
                compressed += '1'; uncompressed.append(byte_stream[count]); count += 1
        return compressed, uncompressed


class MiddleOut:
    @staticmethod
    def middle_out(coefficients, size=2, greater_compression=True, debug=False):
        MiddleOutCompressor.HIGHER_COMPRESSION = greater_compression
        MiddleOutCompressor.LIBRARY_SIZE = size
        orgsize, rl_size, rl = len(coefficients), rlepredict(coefficients), '1'
        if orgsize <= rl_size:
            rl = '0'
        else:
            coefficients = rle(coefficients)
        header, length = positive_binary(size), len(coefficients)
        minbits = minimum_bits(length)
        unary, count = unaryconverter(minbits), positive_binary(length, bits=minbits)
        bitset = rl + header + unary + count + MiddleOutCompressor.byte_compression(coefficients, debug=debug)
        pad = pad_stream(len(bitset))
        num_padded = convertBin(pad, bits=4)
        bitset += ('0' * pad) + num_padded
        return convert_to_list(bitset)

    @staticmethod
    def middle_out_decompress(bitstream, debug=False):
        bitstream = remove_padding(bitstream)
        rl, bitstream = bitstream[0], bitstream[1:]
        header, bitstream = positive_int(bitstream[:8]), bitstream[8:]
        count, unary_count = 0, unaryToInt(bitstream)
        count += unary_count + 1
        length, bitstream = positive_int(bitstream[count:count+unary_count]), bitstream[count+unary_count:]
        MiddleOutCompressor.LIBRARY_SIZE = header
        if rl == '1':
            return rld(MiddleOutDecompressor.decompress(bitstream, length, debug=debug)[0])
        return MiddleOutDecompressor.decompress(bitstream, length, debug=debug)[0]

