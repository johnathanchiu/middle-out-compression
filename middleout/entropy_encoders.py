# entropy encoders for testing
# all rights to the following algorithms belong to respective owners

import lz4.frame as lz
import brotli
import zstd
import lzma
import bz2
import gzip


def lz4compressor(values):
    with lz.LZ4FrameCompressor() as compressor:
        compressed = compressor.begin()
        compressed += compressor.compress(bytes(values))
        compressed += compressor.flush()
    return list(compressed)


def lz4decompressor(values):
    values = bytes(values)
    with lz.LZ4FrameDecompressor() as decompressor:
        decompressed = decompressor.decompress(values)
    return list(decompressed)


def bz2compressor(values):
    return list(bz2.compress(bytes(values)))


def bz2decompressor(values):
    return list(bz2.decompress(bytes(values)))


def lzmacompressor(values):
    return list(lzma.compress(bytes(values)))


def lzmadecomressor(values):
    return list(lzma.decompress(bytes(values)))


def gzipcompressor(values):
    return list(gzip.compress(bytes(values)))


def gzipdecompressor(values):
    return list(gzip.decompress(bytes(values)))


def brotlicompressor(values):
    return list(brotli.compress(bytes(values)))


def brotlidecompressor(values):
    return list(brotli.decompress(bytes(values)))


def zstdcompressor(values):
    return list(zstd.compress(bytes(values), 5))


def zstddecompressor(values):
    return list(zstd.decompress(bytes(values)))

