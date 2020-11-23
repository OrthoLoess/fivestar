"""
Functions for handling data stuff
"""

import numpy as np
import pandas as pd
from fivestar.params import BUCKET_NAME, BUCKET_TRAIN_DATA_PATH, PROJECT_NAME
from google.cloud import storage

def get_data(nrows=10000, local=False, optimize=False, **kwargs):
    """method to get the training data (or a portion of it) from google cloud bucket"""
    # Add Client() here
    filename = 'listings.csv'
    client = storage.Client.from_service_account_json(
        '/Users/ed/code/fivestar/star-project-key.json',
        project=PROJECT_NAME)
    if local:
        path = f"data/{filename}"
    else:
        path = f"gs://{BUCKET_NAME}/{BUCKET_TRAIN_DATA_PATH}/{filename}"
    df = pd.read_csv(path, nrows=nrows, )
    return df


if __name__ == "__main__":
    params = dict(nrows=10,
                  upload=False,
                  local=False,  # set to False to get data from GCP (Storage or BigQuery)
                  optimize=False)
    df = get_data(**params)
    print(df.shape)
