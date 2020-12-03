import time

from fivestar.params import BOROUGHS, PRICES

def decode_amenities(df):
    data = df.copy()
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

def price_tonumerical(df, price_columns):
    '''This function takes as input a dataframe and a list of price column names and
    converts the columnns to floats'''
    for column in price_columns:
        df[[column]] = df[[column]].applymap(str_to_price)
    return df[price_columns]

def str_to_price(strn):
    '''The function converts a price entry from string to float and removes the $ character'''
    if type(strn)== str:
        return float(strn.strip('$').replace(',',''))
    return strn

def house_prices(data):
    house_price_dict = {k: v for k, v in zip(BOROUGHS, PRICES)}
    data['mean_house_prices']= data['neighbourhood_cleansed'].map(house_price_dict)
    return data[['mean_house_prices']]


################
#  DECORATORS  #
################

def simple_time_tracker(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts))
        else:
            print(method.__name__, round(te - ts, 2))
        return result

    return timed
