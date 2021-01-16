def return2DIndex(key, arr, in2D):
    i = [i for i in arr if key in i][in2D]
    return arr.index(i)

#l = list, n = chunk size
def split_array(l, n): 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 