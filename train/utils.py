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


if __name__ =="__main__":
    print impute_list([-1,-1,9.146,7.816,6.486,7.1706,7.8552,8.5398,9.2244], 10)