import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

import fivestar
from fivestar.utils import decode_amenities, price_tonumerical, house_prices
from fivestar.params import KEY_AMENITIES

class AmenitiesEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, key_amenities=KEY_AMENITIES):
        self.key_amenities = key_amenities

    def transform(self, X, y=None):
        data = decode_amenities(X)
        filterables = self.key_amenities
        for item in filterables:
            if isinstance(item, list):
                data[''.join([i for i in item[0] if i.isalpha()])] = 0
            else:
                data[''.join([i for i in item if i.isalpha()])] = 0
        encoding = data.drop(columns='amenities').copy()
        for index,column in enumerate(encoding.columns):
            if isinstance(filterables[index], list):
                for item in filterables[index]:
                    data[column] =  data[['amenities',column]].apply(
                        lambda x: 1 if item.casefold() in x['amenities'] else 1 if x[column] == 1 else 0,
                        axis=1)
            else:
                data[column] =  data[['amenities']].apply(lambda x: 1 if filterables[index].casefold() in x['amenities'] else 0, axis=1)
        return data.drop(columns='amenities')


    def fit(self, X, y=None):
        return self

class AmenitiesCounter(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def transform(self, X, y=None):
        data = X
        amenities = decode_amenities(data)
        data['amenities_count'] = amenities.applymap(lambda x: len(x))
        return data[['amenities_count']]

    def fit(self, X, y=None):
        return self

class CancellationEncoder(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def transform(self, X, y=None):
        data = X
        def recode_cancel(n):
            if n in ('strict_14_with_grace_period','super_strict_30', 'super_strict_60', 'strict'):
                recode = 1
            # elif n in ('moderate','flexible'):
            #     recode = n
            else:
                recode = 0
            return recode
        data['cancellation_strict'] = data['cancellation_policy'].map(recode_cancel)
        return data[['cancellation_strict']]

    def fit(self, X, y=None):
        return self

class RoomTypeEncoder(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def transform(self, X, y=None):
        data = X

        def recode_room(n):
            if n == 'Entire home/apt':
                recode = 1
            else:
                recode = 0
            return recode
        data['room_entire'] = data['room_type'].map(recode_room)
        return data[['room_entire']]

    def fit(self, X, y=None):
        return self

class PriceRatioEncoder(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def transform(self, X, y=None):
        data = X[['price']].join(house_prices(X))
        data['price'] = price_tonumerical(X, ['price'])
        data['price_ratio'] = (data['price'] / (data['mean_house_prices'] / 1e5)**2)
        median = data['price_ratio'].median()
        data['price_ratio'] = data['price_ratio'].map(lambda x: x if x > 0 else median)
        data['price_ratio'] = np.log(data['price_ratio'])
        return data[['price_ratio']]

    def fit(self, X, y=None):
        return self

class AccomodatesToRoomsRatioEncoder(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def transform(self, X, y=None):
        data = X
        data['accommodates_to_rooms_ratio'] = data['accommodates'] / data['bedrooms'].map(lambda x: 1 if x == 0 else x)
        return data[['accommodates_to_rooms_ratio']]

    def fit(self, X, y=None):
        return self

class HostResponseRateEncoder(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def transform(self, X, y=None):
        '''This function takes as input a dataframe ...'''
        df = X
        def str_to_time(strn):
            '''The function converts a price entry from string to float and removes the $ character'''
            if type(strn)== str:
                return float(strn.strip('%'))
            return strn
        for column in ['host_response_rate']:
            df[[column]] = df[[column]].applymap(str_to_time)
        return df[['host_response_rate']]

    def fit(self, X, y=None):
        return self

class CategoricalColumnEncoder(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def transform(self, X, y=None):
        X = X.applymap(lambda x: 1 if x =='t' else (0 if (x == 'f') or np.isnan(x) else x))
        return X

    def fit(self, X, y=None):
        return self

class ScoreDeltaEncoder(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def transform(self, X, y=None, score_column='review_scores_cleanliness'):
        data = X
        length = data.shape[1]
        col_name = score_column[14:] + '_score_delta'
        data[col_name] = data[score_column]\
                                    - data[['review_scores_checkin',
                                                'review_scores_accuracy',
                                                'review_scores_cleanliness',
                                                'review_scores_communication',
                                                'review_scores_location',
                                                'review_scores_value'
                                               ]].mean(axis=1)
        data[col_name] = data[[col_name]].applymap(lambda x: 0.0 if np.isnan(x) else x)
        return data[[col_name]]

    def fit(self, X, y=None):
        return self

