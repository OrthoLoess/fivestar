# -*- coding: UTF-8 -*-
# Copyright (C) 2018 Jean Bizot <jean@styckr.io>
""" Main lib for FiveStar Project
"""
import streamlit as st
from os.path import split
import pandas as pd
import numpy as np
import datetime
from fivestar.data import get_data
from fivestar.params import COLUMNS
from fivestar.model import Model
from fivestar.utils import str_to_price, has_wifi, has_breakfast, cancel_policy_is_strict, is_instant_bookable

pd.set_option('display.width', 200)

class FiveStar():

    def __init__(self):
        self.listings = get_data()
        self.clusters = get_data('clusters')
        self.model = Model().load_model()
        self.build_cluster_info()

    @st.cache(show_spinner=False, persist=True)
    def build_cluster_info(self):
        clusters = self.clusters.set_index('listing_id').join(
            self.listings.set_index('id')[['price','review_scores_cleanliness',
                                            'amenities','instant_bookable',
                                            'cancellation_policy']])
        clusters['price'] = clusters['price'].map(str_to_price)
        clusters['Wifi'] = clusters['amenities'].map(has_wifi)
        clusters['Breakfast'] = clusters['amenities'].map(has_breakfast)
        clusters['instant_bookable'] = clusters['instant_bookable'].map(is_instant_bookable)
        clusters['cancellation_policy'] = clusters['cancellation_policy'].map(cancel_policy_is_strict)

        avgs_per_cluster = clusters.groupby('cluster')[['price','review_scores_cleanliness']].mean()
        cluster_groups = clusters.groupby('cluster')[['Wifi','Breakfast','instant_bookable','cancellation_policy']]
        rates_per_cluster = np.round(100 * cluster_groups.sum() / cluster_groups.count())
        self.cluster_info = avgs_per_cluster.join(rates_per_cluster)

    def get_cluster_id(self, listing_id):
        return self.clusters[self.clusters['listing_id'] == listing_id]['cluster'].values[0]

    def get_cluster_averages(self, cluster_id):
        return self.cluster_info.loc[cluster_id].to_dict()

    def get_listing(self, listing_id):
        """Look up full info for an id and return it as a dict"""
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

        if listing_id:
            self.current_listing = listing_id
            data = listings[listings['id'] == int(listing_id)].to_dict('records')
            return data[0]

    def get_coef_dict(self):
        coefs = self.model.pipeline.named_steps['rgs'].coef_
        coefs_dict = {k:v for k,v in zip(COLUMNS,coefs)}
        return coefs_dict

    @st.cache(show_spinner=False, persist=True)
    def predict_on_new_values(self, listing_id, values={}):
        X_new = self.build_X(listing_id, values)
        return self.model.predict(X_new)[0]

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








if __name__ == '__main__':
    # For introspections purpose to quickly get this functions on ipython
    import fivestar

    # print(' dataframe cleaned')
