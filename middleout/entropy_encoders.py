# entropy encoders for testing
# all rights to the following algorithms belong to respective owners

import lz4.frame as lz
import lzma
import bz2


def lz4compressor(values):
    with lz.LZ4FrameCompressor() as compressor:
        compressed = compressor.begin()
        compressed += compressor.compress(bytes(values))
        compressed += compressor.flush()
    return compressed


def lz4decompressor(values):
    with lz.LZ4FrameDecompressor() as decompressor:
        decompressed = decompressor.decompress(values)
    return decompressed


def bz2compressor(values):
    return list(bz2.compress(bytes(values), 9))


def bz2decompressor(values):
    return list(bz2.decompress(bytes(values)))


def lzmacompressor(values):
    return list(lzma.compress(bytes(values)))


def lzmadecomressor(values):
    return list(lzma.decompress(bytes(values)))