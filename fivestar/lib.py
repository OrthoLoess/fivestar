# -*- coding: UTF-8 -*-
# Copyright (C) 2018 Jean Bizot <jean@styckr.io>
""" Main lib for FiveStar Project
"""

from os.path import split
import pandas as pd
import numpy as np
import datetime
from fivestar.data import get_data
from fivestar.params import COLUMNS
from fivestar.model import Model

pd.set_option('display.width', 200)

class FiveStar():

    def __init__(self):
        self.listings = get_data()
        self.clusters = get_data('clusters')
        self.model = Model().load_model()



    def get_listing(self, listing_id):
        """Look up full info for an id and return it as a dict???"""
        # print(self.listings.shape)
        listings = self.listings
        columns_to_keep = ['review_scores_accuracy',
             'review_scores_cleanliness',
             'review_scores_checkin',
             'review_scores_communication',
             'review_scores_location',
             'review_scores_value',
             'instant_bookable', 'host_identity_verified',
             'amenities', 'price', 'neighbourhood_cleansed',
             'host_listings_count', 'cancellation_policy',
             'host_response_rate', 'accommodates', 'bedrooms', 'room_type',
             ]
        # print(listings)
        if listing_id:
            self.current_listing = listing_id
            data = listings[listings['id'] == int(listing_id)].to_dict('records')
            return data[0]
        #     if type(data) == 'list' and len(data) > 0:
        #         data = data[0]
        #     else:
        #         data = {}
        # else:
        #     data = {}
        # # print(data)
        # return data


    def get_coef_dict(self):
        coefs = self.model.pipeline.named_steps['rgs'].coef_
        coefs_dict = {k:v for k,v in zip(COLUMNS,coefs)}
        return coefs_dict

    def predict_on_new_values(self, listing_id, values={}):
        X_new = self.build_X(listing_id, values)
        return self.model.predict(X_new)



    def build_X(self, listing_id, values):
        listing_attributes = self.get_listing(listing_id)

        for key, value in values.items():
            if key == 'cancellation_policy':
                listing_attributes[key] = 'strict' if value == 'Yes' else 'Other'
            elif key == 'instant_bookable':
                listing_attributes[key] = 't' if value == 'Yes' else 'f'
            elif key == 'Wifi' or key == 'Breakfast':
                if value == 'Yes' and key not in listing_attributes['amenities']:
                    listing_attributes['amenities'] = listing_attributes['amenities'][:-1] + f',{key}' + '}'
                elif value == 'No':
                    listing_attributes['amenities'] = listing_attributes['amenities'].replace(f',{key}', '')
            else:
                listing_attributes[key] = value

        listing_for_df = {k:[v] for k,v in listing_attributes.items()}

        return pd.DataFrame.from_dict(listing_for_df)


def clean_data(data):
    """ clean data
    """

    return data


# def get_listing(listing_id):
#     """Look up full info for an id and return it as a dict???"""
#     listings = get_data()
#     data = listings.loc[listing_id].to_dict('records')[0]
#     return data


if __name__ == '__main__':
    # For introspections purpose to quickly get this functions on ipython
    import fivestar

    # print(' dataframe cleaned')
