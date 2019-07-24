import array


def rle(uncompressed, debug=False):
    counter, prev = 0, None
    sets, setcount = False, 0
    newarr = []
    while counter < len(uncompressed):
        if uncompressed[counter] != prev:
            if sets:
                if debug: print("setcount: ", setcount)
                newarr.append(uncompressed[counter - 1]); newarr.append(setcount)
            newarr.append(uncompressed[counter])
            setcount, sets = 0, False
        else:
            if sets: setcount += 1
            sets = True
        prev = uncompressed[counter]; counter += 1
    if sets: newarr.append(uncompressed[counter - 1]); newarr.append(setcount)
    return newarr


def rld(stream, debug=False):
    counter, prev = 0, None
    arr = array.array('B', [])
    while counter < len(stream):
        if debug: print("arr: ", arr)
        if stream[counter] == prev:
            if debug: print("appending num: ", 1 + stream[counter+1])
            arr += array.array('B', [prev] * (1 + stream[counter+1]))
            counter += 1
        else:
            arr.append(stream[counter])
            prev = stream[counter]
        counter += 1
    return arr
