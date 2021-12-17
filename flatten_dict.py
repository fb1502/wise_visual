def flatten_dict(nested_dict):
    res = {}
    if isinstance(nested_dict, dict):
        for k in nested_dict:
            flattened_dict = flatten_dict(nested_dict[k])
            for key, val in flattened_dict.items():
                key = list(key)
                key.insert(0, k)
                res[tuple(key)] = val
    else:
        res[()] = nested_dict
    return res

def stringify_flatten_dict(unnested_dict):
    res = {}
    for key, value in unnested_dict.items():
        res['_'.join(key)] = value
    return res
