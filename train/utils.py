"""
Utility functions
"""

def get(attr):
    """
    Retrieves the queried attribute value from the config file. Loads the
    config file on first call.
    """
    if not hasattr(get, 'config'):
        with open('config.json') as f:
            get.config = eval(f.read())
    node = get.config
    for part in attr.split('.'):
        node = node[part]
    return node

# datalist is 1-D data list whose missing element should be None
# max_cont_missing_num is the maximum number of elements that are continually missing
def impute_list(datalist, max_cont_missing_num):
    valid_ele_idxs = [i for i, val in enumerate(datalist) if val != -1]

    # all elements are None
    if not valid_ele_idxs:
        return datalist

    prev_valid_ele_idx = None

    new_datalist = list(datalist)

    for valid_ele_idx in valid_ele_idxs:
        if prev_valid_ele_idx is None:
            if valid_ele_idx > 0 and valid_ele_idx <= max_cont_missing_num:
                new_datalist[:valid_ele_idx] = [datalist[valid_ele_idx]] * valid_ele_idx
        else:
            # linear interpolation
            if prev_valid_ele_idx + 1 < valid_ele_idx and valid_ele_idx - prev_valid_ele_idx < max_cont_missing_num + 2:
                start_val = datalist[prev_valid_ele_idx]
                end_val = datalist[valid_ele_idx]
                incre = float(end_val - start_val)/(valid_ele_idx - prev_valid_ele_idx)
                for i in range(1, valid_ele_idx - prev_valid_ele_idx):
                    new_datalist[prev_valid_ele_idx + i] = start_val + i * incre

        prev_valid_ele_idx = valid_ele_idx

    if valid_ele_idx + 1 < len(datalist) and valid_ele_idx + max_cont_missing_num + 1 >= len(datalist):
        new_datalist[valid_ele_idx + 1:] = [datalist[valid_ele_idx]] * (len(datalist) - valid_ele_idx - 1)

    return new_datalist

def unix2week(timelist):
    res = []
    for time in [timelist[4],timelist[6]]:
        date, clock = time.split(" ")
        tmp1 = [0] * 7
        tmp1[int(date.split('-')[-1]) % 7] = 1
        res = res + tmp1
        clock = clock.split(':')
        tmp2 = [0] * 96
        tmp2[int(clock[0]) * 4 + int(int(clock[1]) / 15)] = 1
        res = res + tmp2
    return res

def mov_avg(plot_pred, max_num):
    res = []
    for i, num in enumerate(plot_pred):
        start = max(0, i + 1 - max_num)
        all_sum = 0
        for tmp in plot_pred[start: (i+1)]:
            all_sum = all_sum + tmp
        res.append(all_sum / (i+1-start))
    return res

if __name__ =="__main__":
    #print impute_list([-1,-1,9.146,7.816,6.486,7.1706,7.8552,8.5398,9.2244], 10)
    #print unix2week([0,0,0,0,'2016-11-30 1:23:00','2016-11-30 1:23:00','2016-11-30 1:23:00','2016-11-30 1:23:00'])
    print mov_avg([1,2,3,2,1,4,5,3,2], 2)