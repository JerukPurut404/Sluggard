import sluggard

def get_value_deep_key(data, keys):
    for key in keys:
        data = data[key]
    return data