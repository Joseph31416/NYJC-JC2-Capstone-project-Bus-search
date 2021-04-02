def quick_sort(arr, key, mode):
    if len(arr) > 1:
        pivot = arr.pop(-1)
        lte = []
        gt = []
        while len(arr) > 0:
            x = arr.pop(0)
            if mode == "asc":
                if x[key] <= pivot[key]:
                    lte.append(x)
                else:
                    gt.append(x)
            elif mode == "dsc":
                if x[key] > pivot[key]:
                    lte.append(x)
                else:
                    gt.append(x)
            else:
                raise ValueError
        return quick_sort(lte, key, mode) + [pivot] + quick_sort(gt, key, mode)
    else:
        return arr


def insertion_sort(arr, key, mode):
    n = len(arr)
    for cnt1 in range(1, n):
        if mode == "asc":
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
        elif mode == "dsc":
            if arr[cnt1][key] > arr[cnt1 - 1][key]:
                target = arr.pop(cnt1)
                for cnt2 in range(cnt1):
                    if target[key] > arr[cnt2][key]:
                        arr.insert(cnt2, target)
                        break
        else:
            raise ValueError
    return arr


def find_max_min(arr, key, mode):
    target = None
    for el in arr:
        if target is None:
            target = el[key]
        else:
            if mode == "max":
                if target < el[key]:
                    target = el[key]
            elif mode == "min":
                if target > el[key]:
                    target = el[key]
            else:
                raise ValueError
    return target

