"""
Functions for handling clustering
"""

import numpy as np
import pandas as pd
from fivestar.params import CLUSTER_PERCENTILES


def price_cat(x,pctl):
    '''Transforms an absolute price into a price category, given a list of percentiles'''
    if x <pctl[1]:
        return 'very_cheap'
    elif x >=pctl[1] and x <pctl[3]:
        return 'cheap'
    elif x >=pctl[3] and x <pctl[5]:
        return 'average'
    elif x >=pctl[5] and x <pctl[7]:
        return 'expensive'
    return 'very_expensive'




def clustering(data, percentiles=CLUSTER_PERCENTILES):
    '''Returns a dataframe containing the relevant clustering variables and a second dataframe
    with clustering labels
    '''

    columns=['location', 'price-boroughwise', 'property_type', 'review_scores_rating']
    cluster_df = pd.DataFrame(columns=columns)

    #percentiles=dict()
    neighbourhoods = listings['neighbourhood_cleansed'].unique()
    for neigh in neighbourhoods:
        neigh_listings = listings[listings['neighbourhood_cleansed'] == neigh]
        indices= neigh_listings.index.values.tolist()
        #pctl=[]
        #for p in range(1,10):
        #    pctl.append(np.nanpercentile(neigh_listings['price'], 10*p))
        #neigh_listings['price'].apply(lambda x:price_cat(x,pctl))
        percentiles[neigh] = pctl
        for index in indices:
            cluster_df.loc[index,'price-boroughwise']=price_cat(neigh_listings.loc[index,'price'],pctl)


    bedroom_convert = {0.0: 'small',
                  1.0: 'small',
                  2.0: 'large',
                  3.0: 'large', 4.0: 'large',5.0: 'large',6.0: 'large',7.0: 'large',
                   8.0: 'large',9.0: 'large',10.0: 'large',11.0: 'large',
                   16.0: 'large',22.0: 'large'}
    cluster_df['property_type'] =  data['bedrooms'].map(bedroom_convert)
    cluster_df['room/apt']=data[['room_type']].applymap(lambda x: 'apartment' if x == 'Entire home/apt' else 'room')# if x == 'Private room' else 'Other'))

    cluster_df['location']=data['neighbourhood_cleansed']

    cluster_df['review_scores_rating']=data['review_scores_rating']

    cluster_df['property_type'] = cluster_df.apply(lambda x: 'room' if x['room/apt']== 'room' else x['property_type'], axis=1)
    #cluster_df['listing_id'] = data['id']
    cluster_df=cluster_df.drop(columns='room/apt')
    matching_table = cluster_df.copy()
    matching_table = matching_table.groupby(['location','price-boroughwise','property_type']).count().reset_index().drop(columns='review_scores_rating')
    matching_table['cluster_id'] = matching_table.index
    return cluster_df, matching_table






