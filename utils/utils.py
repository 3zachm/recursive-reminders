import psutil, time, datetime

def return2DIndex(key, arr):
    """Returns the first index of a 2D array for the first
    occurence of the object/variable anywhere in the array.

    Parameters
    ----------
    key : :class:`any`
        Variable or object to find in the array.
    arr : :class:`list`
        2D array to search.

    Returns
    -------
    :class:`int`
        The first index where the key occurs
    """
    i = [i for i in arr if key in i][0]
    return arr.index(i)

def split_array(l, n):
    """Splits array into a 2D array with the given chunk sizes.

    Parameters
    ----------
    l : :class:`list`
        Array to be split.
    n : :class:`int`
        Number of chunks.

    Yields
    -------
    :class:`list`
        The 2D array resulting from the chunks.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_sysuptime():
    return datetime.timedelta(seconds=int(time.time() - psutil.boot_time()))

def get_uptime(boot):
    return datetime.timedelta(seconds=int(time.time() - boot))