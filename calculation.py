import re


def insertion_sort(arr, key):
    """
    :param arr: input contains a list of dictionaries with route, distance and fare as keys
    :param key: input is a string that should be route, distance or fare
    :return: returns a list of dictionaries sorted in ascending order according to the key given
    """
    n = len(arr)
    if key not in ["route", "distance", "fare"]:
        raise KeyError
    if key == "route":
        for cnt1 in range(1, n):
            if int(re.findall(r'\d+', arr[cnt1][key])[0]) < int(re.findall(r'\d+', arr[cnt1 - 1][key])[0]):
                target = arr.pop(cnt1)
                not_found = True
                for cnt2 in range(cnt1):
                    if int(re.findall(r'\d+', target[key])[0]) < int(re.findall(r'\d+', arr[cnt2][key])[0]):
                        arr.insert(cnt2, target)
                        not_found = False
                        break
                if not_found:
                    arr.insert(cnt1, target)
    else:
        for cnt1 in range(1, n):
            if arr[cnt1][key] < arr[cnt1 - 1][key]:
                target = arr.pop(cnt1)
                not_found = True
                for cnt2 in range(cnt1):
                    if target[key] < arr[cnt2][key]:
                        arr.insert(cnt2, target)
                        not_found = False
                        break
                if not_found:
                    arr.insert(cnt1, target)
    return arr


def find_max_min(arr, pos, mode):
    """
    :param arr: input is a list of tuple
    :param pos: input is an integer indicating the position of the element in the tuple for comparison
    :param mode: input is a string indicating the option of finding the minimum or maximum
    :return: returns the maximum value within the list of tuples based on the position given
    """
    target = None
    for el in arr:
        if target is None:
            target = el[pos]
        else:
            if mode == "max":
                if target < el[pos]:
                    target = el[pos]
            elif mode == "min":
                if target > el[pos]:
                    target = el[pos]
            else:
                raise ValueError
    return target


def dist_range(distance):
    """
    :param distance: input is a float of the distance between two destinations
    :return: returns the description of the range for which the distance falls under
    """
    lower = 3.3
    if distance <= 3.2:
        return "0.0 km - 3.2 km"
    while distance >= round(lower, 2) and lower < 40.1:
        lower += 1
    lower -= 1
    if round(lower, 2) == 40.2:
        return "39.3 km - 40.2 km"
    elif lower > 40.1:
        return "Over 40.2 km"
    else:
        return f"{round(lower, 2)} km - {round(lower + 0.9, 2)} km"


