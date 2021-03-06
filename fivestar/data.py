"""
Functions for handling data stuff
"""

import numpy as np
import pandas as pd
from fivestar.params import BUCKET_NAME, BUCKET_TRAIN_DATA_PATH, PROJECT_NAME
from fivestar.params import LISTINGS_COLUMNS
from google.cloud import storage
import gcsfs
from os.path import dirname, isfile
from pathlib import Path
import fivestar


def get_data(file='listings', nrows=None, local=True, optimize=False, path=None, **kwargs):
    """method to get the training data (or a portion of it) from google cloud bucket"""
    if file == 'listings':
        csv_params = dict(
            # index_col='id',
            parse_dates = ['host_since', 'first_review', 'last_review'],
            low_memory = False,
            nrows=nrows,
            usecols=LISTINGS_COLUMNS,
            )
        filename = 'listings.csv'
    elif file == 'clusters':
        csv_params = {}
        filename = 'clusters.csv'
    elif file == 'wordcount':
        csv_params = {}
        filename = 'word_counts2.csv'
    else:
        return None


    if path:
        path = path + filename
    else:
        path = f"{str(Path.home())}/code/OrthoLoess/fivestar/data/jan/{filename}"

    if local and isfile(path):
        df = pd.read_csv(path, **csv_params )
    else:
        # fs = gcsfs.GCSFileSystem(project='PROJECT_NAME', token='/Users/ed/code/fivestar/star-project-key.json')
        # with fs.open(f'{BUCKET_NAME}/{BUCKET_TRAIN_DATA_PATH}/{filename}') as f:
        #     df = pd.read_csv(f, **csv_params)
        # file_url = f'https://data.elandamore.net/fivestar/{BUCKET_TRAIN_DATA_PATH}/{filename}'
        path = f'gs://{BUCKET_NAME}/{BUCKET_TRAIN_DATA_PATH}/{filename}'
        df = pd.read_csv(path, **csv_params )
    if file == 'listings':
        df = df[(df['review_scores_rating'].notna()) & (df['number_of_reviews']>2)]
    return df



if __name__ == "__main__":
    params = dict(local=True)

    df = get_data(**params)
    print(df.shape)
