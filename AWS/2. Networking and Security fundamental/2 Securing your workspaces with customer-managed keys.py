# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Securing your workspaces with customer-managed keys
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
# MAGIC If you would like to follow along with this lab, you will need:
# MAGIC * administrator access to your AWS console, with the ability to create keys
# MAGIC * account with Enterprise pricing tier
# MAGIC * account administrator capabilities in your Databricks account
# MAGIC * an application of your choice to launch REST API commands (cURL, Postman, or others). In this lab we will use cURL within the execution environment provided by an existing workspace

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a key
# MAGIC
# MAGIC Customer-managed keys are KMS keys in your AWS account that you create, own, and manage. You have full control over these KMS keys, including the ability to enable and disable them, maintain their policies, rotating their cryptographic material, and more.
# MAGIC
# MAGIC These keys are useful for a variety of purposes, including the ability to apply them to your workspaces to maintain control of the encryption of all related resources.
# MAGIC
# MAGIC Let's create one now.
# MAGIC
# MAGIC 1. In the AWS KMS console, let's select the region in which we're deploying our workspaces; let's use *us-east-1*.
# MAGIC 1. Click **Create key**.
# MAGIC 1. For **Key type** and **Key usage**, select *Symmetric* and *Encrypt and decrypt* respectively.
# MAGIC 1. In the next page, let's specify and alias (use *dbacademy-test-cmk*).
# MAGIC 1. For now, let's skip key administrotrors and permissions and create the key.
# MAGIC 1. Let's take note of the **Alias** and **ARN** values, as we'll need those to create the key credential momentarily.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Configuring the key policy
# MAGIC
# MAGIC With a key configured, we need to adjust the policy to enable Databricks to encrypt and decrypt using the key. The policy template we provide below is a comprehensive policy that covers all use cases:
# MAGIC * Encrypting data in the control plane
# MAGIC * Encrypting workspace root storage
# MAGIC * Encrypting cluster EBS volumes
# MAGIC
# MAGIC The policy can be trimmed down accordingly if you aren't planning to apply your key across all these use cases.
# MAGIC
# MAGIC 1. Let's click **Switch to policy view**, then click **Edit**.
# MAGIC 1. Now let's insert the following JSON as a new element in the *Statement* array, replacing instances of *<DATABRICKS_ACCOUNT_ID>* with your your actual Databricks account id:
# MAGIC    ```
# MAGIC    {
# MAGIC      "Sid": "Allow Databricks to use KMS key for DBFS",
# MAGIC      "Effect": "Allow",
# MAGIC      "Principal":{
# MAGIC        "AWS":"arn:aws:iam::414351767826:root"
# MAGIC      },
# MAGIC      "Action": [
# MAGIC        "kms:Encrypt",
# MAGIC        "kms:Decrypt",
# MAGIC        "kms:ReEncrypt*",
# MAGIC        "kms:GenerateDataKey*",
# MAGIC        "kms:DescribeKey"
# MAGIC      ],
# MAGIC      "Resource": "*",
# MAGIC      "Condition": {
# MAGIC        "StringEquals": {
# MAGIC          "aws:PrincipalTag/DatabricksAccountId": "<DATABRICKS_ACCOUNT_ID>"
# MAGIC        }
# MAGIC      }
# MAGIC    },
# MAGIC    {
# MAGIC      "Sid": "Allow Databricks to use KMS key for DBFS (Grants)",
# MAGIC      "Effect": "Allow",
# MAGIC      "Principal":{
# MAGIC        "AWS":"arn:aws:iam::414351767826:root"
# MAGIC      },
# MAGIC      "Action": [
# MAGIC        "kms:CreateGrant",
# MAGIC        "kms:ListGrants",
# MAGIC        "kms:RevokeGrant"
# MAGIC      ],
# MAGIC      "Resource": "*",
# MAGIC      "Condition": {
# MAGIC        "StringEquals": {
# MAGIC          "aws:PrincipalTag/DatabricksAccountId": "<DATABRICKS_ACCOUNT_ID>"
# MAGIC        },
# MAGIC        "Bool": {
# MAGIC          "kms:GrantIsForAWSResource": "true"
# MAGIC        }
# MAGIC      }
# MAGIC    },
# MAGIC    {
# MAGIC      "Sid": "Allow Databricks to use KMS key for EBS",
# MAGIC      "Effect": "Allow",
# MAGIC      "Principal": {
# MAGIC        "AWS": "arn:aws:iam::414351767826:root"
# MAGIC      },
# MAGIC      "Action": [
# MAGIC        "kms:Decrypt",
# MAGIC        "kms:GenerateDataKey*",
# MAGIC        "kms:CreateGrant",
# MAGIC        "kms:DescribeKey"
# MAGIC      ],
# MAGIC      "Resource": "*",
# MAGIC      "Condition": {
# MAGIC        "ForAnyValue:StringLike": {
# MAGIC          "kms:ViaService": "ec2.*.amazonaws.com"
# MAGIC        }
# MAGIC      }
# MAGIC    },
# MAGIC    {
# MAGIC      "Sid": "Allow Databricks to use KMS key for managed services in the control plane",
# MAGIC      "Effect": "Allow",
# MAGIC      "Principal": {
# MAGIC        "AWS": "arn:aws:iam::414351767826:root"
# MAGIC      },
# MAGIC      "Action": [
# MAGIC        "kms:Encrypt",
# MAGIC        "kms:Decrypt"
# MAGIC      ],
# MAGIC      "Resource": "*",
# MAGIC      "Condition": {
# MAGIC        "StringEquals": {
# MAGIC          "aws:PrincipalTag/DatabricksAccountId": "<DATABRICKS_ACCOUNT_ID>"
# MAGIC        }
# MAGIC      }
# MAGIC    }
# MAGIC    ```
# MAGIC 1. Finally, let's save our changes.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Using the Accounts API
# MAGIC
# MAGIC In order to use a customer-managed key in a workspace, we must create a key configuration. Managing key configurations and applying them to workspaces cannot currently be done in the account console UI, so we must instead use the Accounts API. This API requires three elements for authentication:
# MAGIC * the Databricks account id
# MAGIC * the username corresponding to a user with account administrator capabilities
# MAGIC * the password for that user
# MAGIC
# MAGIC Of course, you're free to use whichever tool you like to issue the REST API calls but in this lab, we'll use a cluster execution environment to issue the commands using cURL. With that said, if you don't already have access to a cluster and are following along, let's create one now and return to the next cell and run it to perform some setup.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Setting up authentication
# MAGIC
# MAGIC The following cell will establish some text fields at the top of this notebook, which you can fill in with your Databricks account id, username and password. Whenever you update the values of these fields, this will trigger the update of environment variables in the cluster execution environment.

# COMMAND ----------

dbutils.widgets.text(name='account_id', defaultValue='')
dbutils.widgets.text(name='username', defaultValue='')
dbutils.widgets.text(name='password', defaultValue='')

import base64,os

os.environ["DBACADEMY_API_URL"] = f"https://accounts.cloud.databricks.com/api/2.0/accounts/{dbutils.widgets.get('account_id')}"
os.environ["DBACADEMY_API_AUTHENTICATION"] = f"Authorization: Basic {base64.b64encode(('%s:%s' % (dbutils.widgets.get('username'),dbutils.widgets.get('password'))).encode('ascii')).decode('ascii')}"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Querying workspaces
# MAGIC Let's verify we can now authenticate with the REST API by executing the following cells, which displays a list of existing workspaces.

# COMMAND ----------

# MAGIC %sh curl -s -X GET -H "${DBACADEMY_API_AUTHENTICATION}" "${DBACADEMY_API_URL}/workspaces" | json_pp

# COMMAND ----------

# MAGIC %md
# MAGIC This call accomplishes two things:
# MAGIC 1. it validates your authentication information and determines if it provides administrative capabilities
# MAGIC 1. it provides us with information we will need shortly to create a new workspace
# MAGIC
# MAGIC Scrolling through the list, let's locate the workspace we created in the *Deploying a workspace in a customer-managed VPC* lab (or we can use any workspace for that matter). Let's take note of the *credentials_id* and *storage_configuration_id*. Since workspaces can share these configurations, we'll reuse them shortly to create a workspace with our managed key.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a key configuration
# MAGIC
# MAGIC Before we can apply an AWS key to a new or existing workspace, we must make Databricks aware of the key by creating a key configuration. Similar to how credential configurations, storage configurations, and network configurations all bring awareness of AWS constructs into Databricks, key configurations accomplish the same goal for AWS keys. Using the Account console API, let's create a new key configuration. Here we are creating the key for use with both managed services (control plane) and storage (data plane). And in that context, we're also providing for encryption on your cluster's EBS volumes.
# MAGIC
# MAGIC Prior to executing the following cell, be sure to replace <KEY_ARN> and <KEY_ALIAS> to the proper values from the key we created earlier.

# COMMAND ----------

# MAGIC %sh cat << EOF | curl -s -X POST -H "${DBACADEMY_API_AUTHENTICATION}" "${DBACADEMY_API_URL}/customer-managed-keys" -d @- | json_pp
# MAGIC {
# MAGIC   "use_cases": ["STORAGE","MANAGED_SERVICES"],
# MAGIC   "aws_key_info": {
# MAGIC     "key_arn": "<KEY_ARN>",
# MAGIC     "key_alias": "<KEY_ALIAS>",
# MAGIC     "reuse_key_for_cluster_volumes": true
# MAGIC   }
# MAGIC EOF

# COMMAND ----------

# MAGIC %md
# MAGIC Once this executes successfully, take note of the  *customer_managed_key_id*. We will additionally need this value to create our workspace.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a workspace
# MAGIC
# MAGIC Now let's now create a new workspace using our key configuration. Though we've created workspaces before, this time we're using the Account API to do so since key configurations aren't currently handled by the UI.
# MAGIC
# MAGIC Prior to executing the following cell, be sure to replace *&lt;<CREDENTIALS_ID&gt;* and *&lt;STORAGE_CONFIGURATION_ID&gt;* with the values gathered earlier, and replace both instances of *&lt;CSK_ID&gt;* with the customer managed key id you just created.

# COMMAND ----------

# MAGIC %sh cat << EOF | curl -s -X POST -H "${DBACADEMY_API_AUTHENTICATION}" "${DBACADEMY_API_URL}/workspaces" -d @- | json_pp
# MAGIC {
# MAGIC   "workspace_name": "dbacademy_test_workspace_csk",
# MAGIC   "deployment_name": "workspace_csk",
# MAGIC   "credentials_id": "<CREDENTIALS_ID>",
# MAGIC   "storage_configuration_id": "<STORAGE_CONFIGURATION_ID>",
# MAGIC   "managed_services_customer_managed_key_id": "<CSK_ID>",
# MAGIC   "storage_customer_managed_key_id": "<CSK_ID>"
# MAGIC }
# MAGIC EOF

# COMMAND ----------

# MAGIC %md
# MAGIC That's all there is to it! Functionally, this workspace is no different than others; data in both the control and data planes is always always secure and encrypted at rest. In this case, however, we retain full control of the key used in the encryption. Disabling the key in the AWS console will immediately render all data in the the control and data planes inaccessible.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Applying a customer-managed key to an existing workspace
# MAGIC
# MAGIC If the desire is to apply a customer-managed key to an existing workspace, this can be done with a **`PATCH`** request, taking the form as follows. Be sure to substitute
# MAGIC *&lt;WORKSPACE_ID&gt;* with an appropriate value like we saw earlier when listing workpaces. Furthermore, replace both instances of <CSK_ID> with the customer managed key id you just created.
# MAGIC
# MAGIC Note that if you're updating storage encryption, be sure to shutdown any clusters prior to updating, and wait at least 20 minutes after updating to start new clusters or use the DBFS API.

# COMMAND ----------

# MAGIC %sh cat << EOF | curl -s -X PATCH -H "${DBACADEMY_API_AUTHENTICATION}" "${DBACADEMY_API_URL}/workspaces/<WORKSPACE_ID>" -d @- | json_pp
# MAGIC {
# MAGIC   "managed_services_customer_managed_key_id": "<CSK_ID>",
# MAGIC   "storage_customer_managed_key_id": "<CSK_ID>"
# MAGIC }
# MAGIC EOF

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2023 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="https://help.databricks.com/">Support</a>
