

def decode_amenities(df):
    data = df
    def str_to_list(strn):
        row_items = strn[1:-1].split(',')
        for key,item in enumerate(row_items):
            row_items[key] = item.strip('"').casefold()
        return row_items
    return data[['amenities']].applymap(str_to_list)

def has_amenity(df, name, alias=None):
    data = df
    if not alias:
        alias = name
    amenities = decode_amenities(data)
    col_name = f'has_{alias}'
    amenities[col_name] = amenities[['amenities']].applymap(lambda x: 1 if name.casefold() in x else 0)
    return amenities[[col_name]]

def count_amenity(df, name):
    data = has_amenity(df, name)
    return int(data.sum())
