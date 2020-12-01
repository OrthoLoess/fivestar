# -*- coding: UTF-8 -*-
# Copyright (C) 2018 Jean Bizot <jean@styckr.io>
""" Main lib for FiveStar Project
"""

from os.path import split
import pandas as pd
import datetime
from fivestar.data import get_data

pd.set_option('display.width', 200)


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

    print(' dataframe cleaned')
