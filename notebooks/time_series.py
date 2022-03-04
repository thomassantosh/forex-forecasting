# Databricks notebook source
# MAGIC %pip install --upgrade --force-reinstall -r https://aka.ms/automl_linux_requirements.txt

# COMMAND ----------

!pip install azureml-train-automl-runtime

# COMMAND ----------

# Authentication
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import Workspace

# Get service principal
svc_pr = ServicePrincipalAuthentication(
        tenant_id=""
        service_principal_id="",
        service_principal_password="")

# Get the wrkspace config
ws = Workspace(subscription_id="",
        resource_group="",
        workspace_name="",
        auth=svc_pr)

# COMMAND ----------

import logging
import yfinance as yf
inrx= yf.Ticker("INR=X")
df = inrx.history(start='2020-01-01', end='2021-01-31',interval='1d').reset_index()
df.display()

# COMMAND ----------

# df.to_csv('/dbfs/FileStore/sample_data.csv', index=False, encoding='utf-8')

# COMMAND ----------

# Register the dataframe
def pd_dataframe_register(
        df=None,
        def_blob_store=None,
        name=None,
        desc=None):
    """Register pandas dataframe"""
    full_dataset = Dataset.Tabular.register_pandas_dataframe(
            dataframe=df,
            target=def_blob_store,
            name=name,
            description=desc
            )
    full_dataset = full_dataset.with_timestamp_columns('date')

# Create register datasets
def create_register_datasets(df=None,full_dataset_name=None,
        training_set_name=None,
        test_set_name=None
        ):
    """Register the full dataset, including the training/test set"""
#     df = pd.read_csv(source)
    train = df[:-10]
    test = df[-10:]
    def_blob_store = ws.get_default_datastore()
    pd_dataframe_register(df=df, def_blob_store=def_blob_store, name=full_dataset_name)
    pd_dataframe_register(df=train, def_blob_store=def_blob_store,name=training_set_name)
    pd_dataframe_register(df=test, def_blob_store=def_blob_store, name=test_set_name)
    
def model_train(dataset=None, compute_target=None, experiment_name=None):
    """Model and train with AutoML the dataset"""

    forecasting_parameters = ForecastingParameters(
        time_column_name='Date',
        forecast_horizon=12,
        target_rolling_window_size=3, # for simple regression, comment this
        feature_lags='auto',# for simple regression, comment this
        target_lags=12,# for simple regression, comment this
        freq='D',
        validate_parameters=True)

    # Setup the classifier
    automl_settings = {
        "task": 'forecasting',
        "primary_metric":'normalized_root_mean_squared_error',
        "iteration_timeout_minutes": 15,
        "experiment_timeout_hours": 1,#0.25,
#         "compute_target":compute_target,
        "max_concurrent_iterations": 2,
        "featurization": "off",
        #"allowed_models":['AutoArima', 'Prophet'],
        #"blocked_models":['XGBoostClassifier'],
        #"verbosity": logging.INFO,
        "training_data":dataset,#.as_named_input('retrain_dataset'),
        "label_column_name":'Close',
        "n_cross_validations": 3,
        "spark_context":sc,
        "enable_voting_ensemble":True,
        "enable_early_stopping": False,
        "model_explainability":True,
#         "enable_dnn":True,
        "forecasting_parameters": forecasting_parameters
            }

    automl_config = AutoMLConfig(**automl_settings)
    experiment = Experiment(ws, experiment_name)
    remote_run = experiment.submit(automl_config, show_output=True, wait_post_processing=True)
    remote_run.wait_for_completion()
    logging.info(f'Run details: {remote_run}')

    # Convert to AutoMLRun object
    remote_run = AutoMLRun(experiment, run_id=remote_run.id)
    return remote_run

def register_best_model(
        remote_run=None,
        model_name=None,
        model_path=None,
        description=None
        ):
    """Register the best model from the AutoML Run"""
    best_child = remote_run.get_best_child()
    model = best_child.register_model(
            model_name = model_name,
            model_path = model_path,
            description = description,
            )
    logging.info(f"Registered {model_name}, with {description}")
    return model

# COMMAND ----------

from azureml.core import Dataset

full_dataset_name = 'Complete-dataset'
training_set_name = 'Training-dataset'
test_set_name = 'Test-dataset'
create_register_datasets(df=df,full_dataset_name= full_dataset_name,training_set_name= training_set_name,test_set_name = test_set_name)

# COMMAND ----------

# Train the model
from azureml.core.experiment import Experiment
from azureml.automl.core.forecasting_parameters import ForecastingParameters
from azureml.train.automl import AutoMLConfig
from azureml.train.automl.run import AutoMLRun

experiment_name = "time-series-experiment"
ds = Dataset.get_by_name(workspace=ws, name=training_set_name)
remote_run = model_train(dataset=ds,experiment_name=experiment_name)

# COMMAND ----------

# Get the best run and model
best_run, fitted_model = remote_run.get_output()

# COMMAND ----------

# Display the test data
dt = Dataset.get_by_name(workspace=ws, name='Test-dataset')
dt = dt.to_pandas_dataframe()
dt.display()

# COMMAND ----------

# Forecast the test period to see forecast
# Note weekend gaps
fitted_model.forecast(dt, ignore_data_errors=True)

# COMMAND ----------


