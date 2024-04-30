# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Using the Account API
# MAGIC
# MAGIC In this lab you will learn how to:
# MAGIC * Create your own AWS customer-managed keys
# MAGIC * Apply an AWS key to a new workspace to provide security across:
# MAGIC    * the data plane (root storage and cluster local storage)
# MAGIC    * the control plane
# MAGIC * Apply an AWS key to an existing workspace

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prerequisites
# MAGIC
# MAGIC If you would like to follow along with this lab, you will need account administrator capabilities in your Databricks account. 
# MAGIC
# MAGIC You'll also need a tool or environment to issue REST API calls. In this lab, we'll use a cluster execution environment to issue the commands using cURL though you can use cURL or a similar tool in your own environment if you like.
# MAGIC
# MAGIC If you're following along and leveraging a cluster execution environment, then let's create a cluster if we don't have one already, then attach it to this notebook.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setting up authentication
# MAGIC
# MAGIC The Account API requires three elements for authentication:
# MAGIC * the Databricks account id
# MAGIC * the username corresponding to a user with account administrator capabilities
# MAGIC * the password for that user
# MAGIC
# MAGIC The following cell will establish some text fields at the top of this notebook to provide this information. When you enter your credentials into these fields, code will execute on the cluster to set up environment variables with this information. This setup greatly simplifies the API calls we will be making.
# MAGIC
# MAGIC If you're using your own tool, then you can forego the following cell and configure your tool as follows:
# MAGIC * Use **Basic** authentication with the username and password separated by a colon (:)
# MAGIC * Use a base URL of *https://accounts.cloud.databricks.com/api/2.0/accounts/* followed by your Databricks account id; all API endpoints will be added to the end of this base URL

# COMMAND ----------

dbutils.widgets.text(name='account_id', defaultValue='')
dbutils.widgets.text(name='username', defaultValue='')
dbutils.widgets.text(name='password', defaultValue='')

import base64,os

os.environ["DBACADEMY_API_URL"] = f"https://accounts.cloud.databricks.com/api/2.0/accounts/{dbutils.widgets.get('account_id')}"
os.environ["DBACADEMY_API_AUTHENTICATION"] = f"Authorization: Basic {base64.b64encode(('%s:%s' % (dbutils.widgets.get('username'),dbutils.widgets.get('password'))).encode('ascii')).decode('ascii')}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Querying workspaces
# MAGIC Let's issue the following call, which displays a list of existing workspaces. This call accomplishes two things:
# MAGIC 1. it provides us with useful information that we can use later in the exercise
# MAGIC 1. it validates your authentication information and determines if it provides administrative capabilities
# MAGIC
# MAGIC If using your own tool, specify the **`GET`** method and an API endpoint of */workspaces*.

# COMMAND ----------

# MAGIC %sh curl -s -X GET -H "${DBACADEMY_API_AUTHENTICATION}" "${DBACADEMY_API_URL}/workspaces" | json_pp

# COMMAND ----------

# MAGIC %md
# MAGIC Scrolling through the response, let's locate the workspace that we can experiement with. Let's take note of the *credentials_id* and *storage_configuration_id*. Since workspaces can share these configurations, we'll reuse them momentarily to create a new workspace.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a workspace
# MAGIC
# MAGIC Let's create a new workspace. Though we may have created workspaces before using the account console, this time we're doing it programmatically using the Account API.
# MAGIC
# MAGIC Prior to executing the following cell, be sure to perform the following subsitutions in the JSON payload:
# MAGIC * replace *&lt;CREDENTIALS_ID&gt;* and *&lt;STORAGE_CONFIGURATION_ID&gt;* with the values gathered earlier
# MAGIC * modify the value of *aws_region* to match the value of the workspace you're copying from, if it's not *us-east-1*
# MAGIC
# MAGIC If using your own tool, configure it as follows:
# MAGIC * Use an API endpoint of */workspaces*
# MAGIC * Use the **`POST`** method
# MAGIC * Include the modified JSON payload from the following cell in your request

# COMMAND ----------

# MAGIC %sh cat << EOF | curl -s -X POST -H "${DBACADEMY_API_AUTHENTICATION}" "${DBACADEMY_API_URL}/workspaces" -d @- | json_pp
# MAGIC {
# MAGIC   "workspace_name": "dbacademy-test-workspace-api",
# MAGIC   "deployment_name": "dbacademy-test-workspace-api",
# MAGIC   "aws_region" : "us-east-1",
# MAGIC   "credentials_id": "<CREDENTIALS_ID>",
# MAGIC   "storage_configuration_id": "<STORAGE_CONFIGURATION_ID>"
# MAGIC }
# MAGIC EOF

# COMMAND ----------

# MAGIC %md
# MAGIC ### Monitoring a workspace
# MAGIC
# MAGIC You can query an individual workspace with a simple **`GET`** request as follows. This is useful for querying information for just a single workspace, or to monitor the status of the workspace we just requested. Be sure to replace *&lt;WORKSPACE_ID&gt;* with the value from the response to creating the workspace earlier.

# COMMAND ----------

# MAGIC %sh curl -s -X GET -H "${DBACADEMY_API_AUTHENTICATION}" "${DBACADEMY_API_URL}/workspaces/<WORKSPACE_ID>" | json_pp

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC
# MAGIC Here we've presented a few examples of Account API usage. This by no means is an exhaustive list. For more information please refer to the <a href="https://docs.databricks.com/dev-tools/api/latest/account.html" target="_blank">documentation</a>.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2023 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="https://help.databricks.com/">Support</a>
