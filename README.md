# forex-forecasting 
A repo to forecast forex currency rates, with the use of Azure Databricks and the AutoML capabilities from Azure Machine Learning.

## Pending Build
- Automation of the .netrc file
- Inclusion of additional services: Key Vault, ADF, Power BI.

## Notes
- Setup with `python=3.7`
- Requires a `sub.env` file in the root, with a following line of code: `SUB_ID=<subscription_id>`.

### Documentation
- For AutoML, Databricks https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-databricks-automl-environment
- Paper on forecasting forex http://cs229.stanford.edu/proj2018/report/76.pdf
- How to configure databricks for automl https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-databricks-automl-environment
- Classification with AutoML in Databricks https://github.com/Azure/azureml-examples/blob/main/python-sdk/tutorials/automl-with-databricks/automl-databricks-local-01.ipynb
