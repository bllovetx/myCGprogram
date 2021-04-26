def mix_point(pA:list, pB:list, t:float):
    assert(len(pA) == len(pB))
    mixed = []
    for i in range(len(pA)):
        mixed.append(t*pA[i] + (1-t)*pB[i])
    return mixed


print(mix_point([1, 3], [2, 6], 0.2))