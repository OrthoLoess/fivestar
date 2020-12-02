# -*- coding: UTF-8 -*-
# Copyright (C) 2018 Jean Bizot <jean@styckr.io>
""" Main lib for FiveStar Project
"""

from os.path import split
import pandas as pd
import datetime
from fivestar.data import get_data

pd.set_option('display.width', 200)

class FiveStar():

    def __init__(self):
        self.listings = get_data()
        self.clusters = get_data('clusters')

    def get_listing(self, listing_id):
        """Look up full info for an id and return it as a dict???"""
        # print(self.listings.shape)
        listings = self.listings
        # print(listings)
        if listing_id:
            data = listings[listings['id'] == int(listing_id)].to_dict('records')

            if  len(data) > 0:
                data = data[0]

            else:
                data = {}
        else:
            data = {}
        # print(data)
        return data


def clean_data(data):
    """ clean data
    """

    return data


def get_listing(listing_id):
    """Look up full info for an id and return it as a dict???"""
    listings = get_data()
    data = listings.loc[listing_id].to_dict('records')[0]
    return data


if __name__ == '__main__':
    # For introspections purpose to quickly get this functions on ipython
    import fivestar
    fs = FiveStar()
    listing_data = fs.get_listing(53242)
    for key, value in listing_data.items():
        print(f"{key} is {value}")
    print(' dataframe cleaned')
