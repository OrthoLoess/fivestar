"""
Functions for handling clustering
"""

import numpy as np
import pandas as pd
from fivestar.params import CLUSTER_PERCENTILES
from fivestar.data import get_data


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

def property_cat(ptype, psize):
    '''Transforms property type and size into a property cluster category'''
    if ptype != 'Entire home/apt':
        return 'room'
    elif psize < 2:
        return 'small'
    return 'large'


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
    cluster_df['listing_id'] = data['id']
    cluster_df['lat'] = data['latitude']
    cluster_df['lon'] = data['longitude']
    cluster_df=cluster_df.drop(columns='room/apt')
    matching_table = cluster_df.drop(columns=['listing_id']).copy()
    matching_table = matching_table.groupby(['location','price-boroughwise','property_type']).count().reset_index().drop(columns='review_scores_rating')
    matching_table['cluster_id'] = matching_table.index
    return cluster_df, matching_table


def user_ranking(location, price, size, listing_id, clusters, percentiles=CLUSTER_PERCENTILES):
    '''Takes as input a neighborhood, a price, a listing property type, the listing id and the clusters dataframe
    returns:
    - the listing's ranking within its cluster
    - the cluster's average rating
    - the cluster size
    '''

    price_c=price_cat(price,percentiles[location])

    cluster = clusters[(clusters['location'] == location ) &  (clusters['price-boroughwise'] == price_c ) &\
              (clusters['property_type'] == size )\
            ].copy()
    cluster['ranking'] = cluster['review_scores_rating'].rank(method='min',ascending=False)
    cluster_average = cluster['review_scores_rating'].mean()
    user_rank =int(cluster[cluster['listing_id']== listing_id].iloc[0].loc['ranking'])
    return user_rank, cluster_average, cluster.shape[0]




def top_rated(location, price, size, clusters, top=10, percentiles=CLUSTER_PERCENTILES):
    '''Takes as input a neighborhood, a price, a listing property type,  and the clusters dataframe
    returns:
    - a list with the ids of the top-rated listings in the cluster
    '''

    price_c=price_cat(price,percentiles[location])

    cluster = clusters[(clusters['location'] == location ) &  (clusters['price-boroughwise'] == price_c ) &\
              (clusters['property_type'] == size )\
            ].copy()
    cluster['ranking'] = cluster['review_scores_rating'].rank(method='min',ascending=False)

    sorted_cluster = cluster.sort_values(by='ranking')

    nrows= round(cluster.shape[0]/ top)

    return sorted_cluster.iloc[:nrows].listing_id



def cluster_selection(location, price, size, clusters, percentiles=CLUSTER_PERCENTILES):
    '''Takes as input a neighborhood, a price, a listing property type,  and the clusters dataframe
    returns:
    - the cluster to which the listings belongs
    '''
    price_c=price_cat(price,percentiles[location])
    cluster = clusters[(clusters['location'] == location ) &  (clusters['price-boroughwise'] == price_c ) &\
              (clusters['property_type'] == size )\
            ].copy()
    return cluster


def cluster_coordinates(location, price, ptype, psize, clusters, percentiles=CLUSTER_PERCENTILES):
    '''Takes as input a neighborhood, a price, a listing property type, the clusters dataframe and the raw dataframe
    returns:
    - the geographical coordinates of all listings in the same cluster
    '''
    size_c = property_cat(ptype, psize)
    price_c=price_cat(price,percentiles[location])
    cluster = clusters[(clusters['location'] == location ) &  (clusters['price-boroughwise'] == price_c ) &\
              (clusters['property_type'] == size_c )\
            ].copy()

    #indices = cluster.index.values.tolist()
    coordinates = cluster[['lat','lon']]
    return coordinates

def get_cluster_coords(location, price, ptype, psize):

    # get clusters,listings etc
    clusters = get_data('clusters')
    #listings = get_data('listings')
    coordinates = cluster_coordinates(location, price, ptype, psize, clusters)

    return coordinates




