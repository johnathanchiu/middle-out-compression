from collections import Counter
from middleOut.MiddleOut import MiddleOutUtils

class BinaryMiddleOut:

    @staticmethod
    def compressor(values):
        leading = MiddleOutUtils.max_key(Counter(values))
        move_to_back = ''
        for i in values:
            if i == leading:
                move_to_back += leading
            else:
                move_to_back += i
        return
