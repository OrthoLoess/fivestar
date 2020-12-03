import multiprocessing
import time
import warnings
from tempfile import mkdtemp

import category_encoders as ce
import joblib
import mlflow
import numpy as np
import pandas as pd

from fivestar.encoders import *
from fivestar.utils import simple_time_tracker

from memoized_property import memoized_property
from mlflow.tracking import MlflowClient
from psutil import virtual_memory
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, Ridge, LinearRegression
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler
from termcolor import colored

# Mlflow wagon server
MLFLOW_URI = "https://mlflow.lewagon.co/"


class Trainer(object):
    # Mlflow parameters identifying the experiment, you can add all the parameters you wish
    ESTIMATOR = "Ridge"
    EXPERIMENT_NAME = "FiveStar"

    def __init__(self, X=None, y=None, **kwargs):
        """
        FYI:
        __init__ is called every time you instatiate Trainer
        Consider kwargs as a dict containig all possible parameters given to your constructor
        Example:
            TT = Trainer(nrows=1000, estimator="Linear")
               ==> kwargs = {"nrows": 1000,
                            "estimator": "Linear"}
        :param X:
        :param y:
        :param kwargs:
        """
        self.pipeline = None
        self.kwargs = kwargs
        self.grid = kwargs.get("gridsearch", False)  # apply gridsearch if True
        self.local = kwargs.get("local", True)  # if True training is done locally
        self.optimize = kwargs.get("optimize", False)  # Optimizes size of Training Data if set to True
        self.mlflow = kwargs.get("mlflow", False)  # if True log info to nlflow
        self.experiment_name = kwargs.get("experiment_name", self.EXPERIMENT_NAME)  # cf doc above
        self.model_params = None  # for
        self.X_train = X
        self.y_train = y
        del X, y
        self.split = self.kwargs.get("split", False)  # cf doc above
        if self.split:
            self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(self.X_train, self.y_train,
                                                                                  test_size=0.25,
                                                                                  random_state=42)
        self.nrows = self.X_train.shape[0]  # nb of rows to train on
        self.log_kwargs_params()
        self.log_machine_specs()

    def get_estimator(self):
        estimator = self.kwargs.get("estimator", self.ESTIMATOR)
        if estimator == "Linear":
            model = LinearRegression()
        else:
            model = Ridge(alpha=50)
        estimator_params = self.kwargs.get("estimator_params", {})
        self.mlflow_log_param("estimator", estimator)
        model.set_params(**estimator_params)
        print(colored(model.__class__.__name__, "red"))
        return model

    def set_pipeline(self):
        memory = self.kwargs.get("pipeline_memory", None)
        dist = self.kwargs.get("distance_type", "euclidian")
        feateng_default = ['amenities', 'amenity_count', 'categoricals',
                            'price_ratio', 'listing_count', 'cancellation',
                            'response_rate', 'room_ratio', 'cleanliness_delta',
                            'room_type']
        feateng_steps = self.kwargs.get("feateng", feateng_default)
        if memory:
            memory = mkdtemp()

        # Define feature engineering pipeline blocks here
        pipe_categoricals = make_pipeline(CategoricalColumnEncoder())
        pipe_amenities = make_pipeline(AmenitiesEncoder())
        pipe_amenity_count = make_pipeline(AmenitiesCounter(), StandardScaler())
        pipe_price_ratio = make_pipeline(PriceRatioEncoder(), StandardScaler())
        pipe_host_listings_count = make_pipeline(
            SimpleImputer(strategy='constant', fill_value=1), StandardScaler())
        pipe_cancellation = make_pipeline(CancellationEncoder())
        pipe_response_rate = make_pipeline(
            HostResponseRateEncoder(),
            SimpleImputer(strategy='median'),
            StandardScaler())
        pipe_room_ratio = make_pipeline(
            AccomodatesToRoomsRatioEncoder(),
            SimpleImputer(strategy='mean'),
            StandardScaler())
        pipe_cleanliness_delta = make_pipeline(ScoreDeltaEncoder(), StandardScaler())
        pipe_room_type = make_pipeline(RoomTypeEncoder())

        review_columns = ['review_scores_accuracy',
             'review_scores_cleanliness',
             'review_scores_checkin',
             'review_scores_communication',
             'review_scores_location',
             'review_scores_value']

        # Define default feature engineering blocs
        feateng_blocks = [
            ('amenities', pipe_amenities, ['amenities']),
            ('amenity_count', pipe_amenity_count, ['amenities']),
            ('categoricals', pipe_categoricals, ['instant_bookable', 'host_identity_verified']),
            ('price_ratio', pipe_price_ratio, ['price', 'neighbourhood_cleansed']),
            ('listing_count', pipe_host_listings_count, ['host_listings_count']),
            ('cancellation', pipe_cancellation, ['cancellation_policy']),
            ('response_rate', pipe_response_rate, ['host_response_rate']),
            ('room_ratio', pipe_room_ratio, ['accommodates', 'bedrooms']),
            ('cleanliness_delta', pipe_cleanliness_delta, review_columns),
            ('room_type', pipe_room_type, ['room_type']),
        ]
        # Filter out some bocks according to input parameters
        for bloc in feateng_blocks:
            if bloc[0] not in feateng_steps:
                feateng_blocks.remove(bloc)

        features_encoder = ColumnTransformer(feateng_blocks, n_jobs=None, remainder="drop")

        self.pipeline = Pipeline(steps=[
            ('features', features_encoder),
            ('rgs', self.get_estimator())], memory=memory)


    def predict(self, X):
        return self.pipeline.predict(X)

    def load_model(self):
        self.pipeline = joblib.load('model.joblib')

    def add_grid_search(self):
        """"
        Apply Gridsearch on self.params defined in get_estimator
        {'rgs__n_estimators': [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)],
          'rgs__max_features' : ['auto', 'sqrt'],
          'rgs__max_depth' : [int(x) for x in np.linspace(10, 110, num = 11)]}
        """
        # Here to apply ramdom search to pipeline, need to follow naming "rgs__paramname"
        params = {"rgs__" + k: v for k, v in self.model_params.items()}
        self.pipeline = RandomizedSearchCV(estimator=self.pipeline, param_distributions=params,
                                           n_iter=20,
                                           cv=3,
                                           verbose=1,
                                           random_state=42,
                                           n_jobs=None)

    # @simple_time_tracker
    def train(self, gridsearch=False):
        tic = time.time()
        self.set_pipeline()
        if gridsearch:
            self.add_grid_search()
        self.pipeline.fit(self.X_train, self.y_train)
        # mlflow logs
        self.mlflow_log_metric("train_time", int(time.time() - tic))

    def evaluate(self):
        r2_train = self.compute_r2(self.X_train, self.y_train)
        self.mlflow_log_metric("r2_train", r2_train)
        if self.split:
            r2_val = self.compute_r2(self.X_val, self.y_val, show=True)
            self.mlflow_log_metric("r2_val", r2_val)
            print(colored("rmse train: {} || rmse val: {}".format(r2_train, r2_val), "blue"))
        else:
            print(colored("rmse train: {}".format(r2_train), "blue"))

    def compute_r2(self, X_test, y_test, show=False):
        if self.pipeline is None:
            raise ("Cannot evaluate an empty pipeline")
        r2 = self.pipeline.score(X_test, y_test)
        return round(r2, 4)

    def save_model(self, upload=True, auto_remove=True):
        """Save the model into a .joblib and upload it on Google Storage /models folder
        HINTS : use sklearn.joblib (or jbolib) libraries and google-cloud-storage"""
        joblib.dump(self.pipeline, 'model.joblib')
        # print(colored("model.joblib saved locally", "green"))

        # Add upload of model.joblib to storage here
        # version = self.kwargs.get('version', None)
        # if version:
        #     storage_upload(model_version=version)
        # else:
        #     storage_upload()

    ### MLFlow methods
    @memoized_property
    def mlflow_client(self):
        mlflow.set_tracking_uri(MLFLOW_URI)
        return MlflowClient()

    @memoized_property
    def mlflow_experiment_id(self):
        try:
            return self.mlflow_client.create_experiment(self.experiment_name)
        except BaseException:
            return self.mlflow_client.get_experiment_by_name(self.experiment_name).experiment_id

    @memoized_property
    def mlflow_run(self):
        return self.mlflow_client.create_run(self.mlflow_experiment_id)

    def mlflow_log_param(self, key, value):
        if self.mlflow:
            self.mlflow_client.log_param(self.mlflow_run.info.run_id, key, value)

    def mlflow_log_metric(self, key, value):
        if self.mlflow:
            self.mlflow_client.log_metric(self.mlflow_run.info.run_id, key, value)

    def log_estimator_params(self):
        reg = self.get_estimator()
        self.mlflow_log_param('estimator_name', reg.__class__.__name__)
        params = reg.get_params()
        for k, v in params.items():
            self.mlflow_log_param(k, v)

    def log_kwargs_params(self):
        if self.mlflow:
            for k, v in self.kwargs.items():
                self.mlflow_log_param(k, v)

    def log_machine_specs(self):
        cpus = multiprocessing.cpu_count()
        mem = virtual_memory()
        ram = int(mem.total / 1000000000)
        self.mlflow_log_param("ram", ram)
        self.mlflow_log_param("cpus", cpus)


if __name__ == "__main__":
    warnings.simplefilter(action='ignore', category=FutureWarning)
    # Get and clean data
    experiment = "[GB] [London] [EdLandamore] FiveStar v1"
    params = dict(nrows=None,
                  upload=False, # upload model.job lib to strage if set to True
                  local=True,  # set to False to get data from GCP Storage
                  gridsearch=False,
                  optimize=False,
                  estimator="Ridge",
                  mlflow=True,  # set to True to log params to mlflow
                  experiment_name=experiment,
                  version='ridge_v1')
    print("############   Loading Data   ############")
    df = get_data(**params)
    # df = clean_df(df)
    y_train = df["review_scores_rating"]
    X_train = df.drop("review_scores_rating", axis=1)
    del df
    print("shape: {}".format(X_train.shape))
    print("size: {} Mb".format(X_train.memory_usage().sum() / 1e6))
    # Train and save model, locally and
    t = Trainer(X=X_train, y=y_train, **params)
    del X_train, y_train
    print(colored("############  Training model   ############", "red"))
    t.train()
    print(colored("############  Evaluating model ############", "blue"))
    t.evaluate()
    print(colored("############   Saving model    ############", "green"))
    t.save_model()
