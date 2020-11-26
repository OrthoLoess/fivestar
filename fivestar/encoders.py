import pandas as pd
import numpy as np

import fivestar
from fivestar.utils import decode_amenities
from fivestar.params import KEY_AMENITIES

class AmenitiesEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, key_amenities=KEY_AMENITIES):
        self.time_column = time_column
        self.time_zone_name = time_zone_name

    def transform(self, X, y=None):
        assert isinstance(X, pd.DataFrame)
        X.index = pd.to_datetime(X[self.time_column])
        X.index = X.index.tz_convert(self.time_zone_name)
        X["dow"] = X.index.weekday
        X["hour"] = X.index.hour
        X["month"] = X.index.month
        X["year"] = X.index.year
        return X[["dow", "hour", "month", "year"]].reset_index(drop=True)

    def fit(self, X, y=None):
        return self
