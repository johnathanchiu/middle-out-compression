# Run length encoders for Middle-Out
# © Johnathan Chiu, 2019

import array
from middleout.utils import positive_int


def rle(uncompressed, debug=False):
    counter, prev = 0, None
    sets, setcount = False, 0
    newarr = array.array('B', [])
    while counter < len(uncompressed):
        if uncompressed[counter] != prev:
            if sets:
                if debug: print("setcount: ", setcount)
                if setcount > 255:
                    setcount -= 255; newarr.append(uncompressed[counter - 1]); newarr.append(255)
                    while setcount > 257:
                        newarr += array.array('B', [uncompressed[counter - 1]] * 2); newarr.append(255)
                        setcount -= 257
                    if setcount >= 2:
                        if setcount == 1: newarr.append(uncompressed[counter - 1])
                        else: newarr += array.array('B', [uncompressed[counter - 1]] * 2); newarr.append(setcount - 2)
                else:
                    newarr.append(uncompressed[counter - 1]); newarr.append(setcount)
            newarr.append(uncompressed[counter])
            setcount, sets = 0, False
        else:
            if sets: setcount += 1
            sets = True
        prev = uncompressed[counter]; counter += 1
    if sets:
        if debug: print("setcount: ", setcount)
        if setcount > 255:
            setcount -= 255; newarr.append(uncompressed[counter - 1]); newarr.append(255)
            while setcount >= 257:
                newarr += array.array('B', [uncompressed[counter - 1]] * 2); newarr.append(255)
                setcount -= 257
            if setcount >= 1:
                if setcount == 1: newarr.append(uncompressed[counter - 1])
                else: newarr += array.array('B', [uncompressed[counter - 1]] * 2); newarr.append(setcount - 2)
        else:
            newarr.append(uncompressed[counter - 1]); newarr.append(setcount)
    return newarr


def rld(stream, debug=False):
    counter, prev, fore = 0, None, True
    arr = array.array('B', [])
    while counter < len(stream):
        if debug: print("arr: ", arr); print("counter value: ", stream[counter])
        if stream[counter] == prev and fore:
            if debug: print("appending num: ", 1 + stream[counter+1])
            arr += array.array('B', [prev] * (1 + stream[counter+1]))
            counter += 1; fore = False
        else:
            if debug: print("new counter")
            arr.append(stream[counter]); prev = stream[counter]; fore = True
        counter += 1
    return arr


def compressed_count(values, length):
    trace = False
    count, counter, prev = 0, 0, None
    while count < length:
        print(count); print(positive_int(values[counter:counter+8]))
        if positive_int(values[counter:counter+8]) == prev and not trace:
            print(positive_int(values[counter+8:counter+16]))
            trace = True; count += 1 + positive_int(values[counter+8:counter+16]); counter += 8
        else: trace = False; count += 1
        counter += 8
        prev = positive_int(values[counter:counter+8])
    return counter // 8

