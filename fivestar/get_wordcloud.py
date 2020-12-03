import pandas as pd
from wordcloud import WordCloud
from fivestar.data import get_data


def get_wordcloud(cluster_id):

    # the dataframe wordcounts_df contains the most common 2 words associations
    # and associated counts for the clusters in label_list as well as
    # across all clusters (if the cluster label for listing_id is not in this
    # list, the wordcloud will be based on the word counts calculated across
    # all clusters)
    label_list = ['L:Westminster_P:very_cheap_S:room',\
                'L:Tower Hamlets_P:very_cheap_S:room',\
                'L:Tower Hamlets_P:cheap_S:room',\
                'L:Camden_P:very_cheap_S:room',\
                'L:Lambeth_P:cheap_S:room',\
                'L:Camden_P:cheap_S:room',\
                'L:Southwark_P:cheap_S:room',\
                'L:Hammersmith and Fulham_P:very_cheap_S:room',\
                'L:Southwark_P:very_cheap_S:room',\
                'L:Lambeth_P:very_cheap_S:room',\
                'L:Westminster_P:cheap_S:small',\
                'L:Hackney_P:cheap_S:room',\
                'L:Islington_P:very_cheap_S:room',\
                'L:Kensington and Chelsea_P:very_cheap_S:room',\
                'L:Westminster_P:cheap_S:room',\
                'L:Islington_P:cheap_S:room',\
                'L:Westminster_P:very_expensive_S:large',\
                'L:Hackney_P:very_cheap_S:room',\
                'L:Westminster_P:expensive_S:large',\
                'L:Westminster_P:average_S:small',\
                'L:Wandsworth_P:cheap_S:room']

    wordcounts_df = get_data('wordcount')
    # If cluster_id not in above list, set to 'All'. The wordcloud will be based
    # on the word associations calculated across all clusters
    if cluster_id not in label_list:
        cluster_id = 'All'

    # Extract word_counts from wordcl_df for cluster_id
    word_counts = wordcounts_df.loc[wordcounts_df['cluster'] == cluster_id]

    # Turn into right format for wordcloud and create wordcloud
    word_counts = pd.Series(word_counts['count'].to_list(), index = word_counts['quotes'].to_list())
    wordcloud = WordCloud(background_color="white",collocation_threshold=5).generate_from_frequencies(word_counts)

    return wordcloud
