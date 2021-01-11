def return2DIndex(key, arr, in2D):
    i = [i for i in arr if key in i][in2D]
    return arr.index(i)