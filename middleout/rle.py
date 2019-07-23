def rle(uncompressed):
    counter, prev = 0, None
    sets, setcount = False, 0
    newarr = []
    while counter < len(uncompressed):
        if prev == uncompressed[counter]:
            if sets:
                newarr.append(prev)
                setcount += 1
            set = True
        prev = uncompressed[counter]
        counter += 1
    return


def rld(stream):

    return
