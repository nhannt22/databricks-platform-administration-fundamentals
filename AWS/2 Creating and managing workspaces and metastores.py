# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Creating and managing workspaces and metastores
# MAGIC
# MAGIC In this lab you will learn how to use the account console to:
# MAGIC * Create and manage workspaces
# MAGIC * Create and manage metastores
# MAGIC * Manage metastore assignments

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prerequisites
# MAGIC
# MAGIC If you would like to follow along with this demo, you will need:
# MAGIC * account administrator capabilities in your Databricks account in order to access the account console
# MAGIC * resources created as a product of performing the *Supporting Databricks workspaces and metastores* lab. Specifically, you will need:
# MAGIC    * a bucket path and IAM role ARN to create a metastore
# MAGIC    * a credential cofiguration and storage configuration to create a workspace 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Metastores
# MAGIC
# MAGIC A metastore is the top-level container of data objects in Unity Catalog, the data governance solution for the Databricks Lakehouse platform. The metastore contains metadata about your tables and, in the case of managed tables, the table data itself.
# MAGIC
# MAGIC Account administrators create metastores and assign them to workspaces to allow workloads in those workspaces to access the data represented in the metastore. This can be done in the account console, through REST APIs, or using an automation framework like <a href="https://registry.terraform.io/providers/databrickSlabs/databricks/latest/docs" target="_blank">Terraform</a>. In this demo, we will explore the creation and management of metastores interactively using the account console.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating a metastore
# MAGIC
# MAGIC With all the supporting resources in place, we are now ready to create a metastore.
# MAGIC
# MAGIC 1. In the account console, let's click on the **Data** icon in the left sidebar. This will display a list of currently created metastores.
# MAGIC 1. Let's click **Create metastore**.
# MAGIC 1. Let's provide a name for the metastore. Only account administrators will have visibility into the metastore name; users will only see catalogs, schemas and other entities within the metastore. In this example I will use the name *dbacademy-test-metastore*.
# MAGIC 1. Since some metadata is maintained in the control plane, the **Region** setting allows us to align the storage of that metadata with the bucket backing this metastore. So let's choose the same region we used when creating the bucket backing the metastore.
# MAGIC 1. Specify the path of the bucket created for the metastore (for example, *s3://dbacademy-test-metastore-bucket*).
# MAGIC 1. Let's paste the **ARN** of the IAM role we created for the metastore bucket.
# MAGIC 1. Finally, let's click **Create**.
# MAGIC
# MAGIC From here we can assign the newly created metastore to any of the workspaces available in this account. But for now let's click **Skip** as this can be done at any time in the future.
# MAGIC
# MAGIC While we're here, let's configure the metastore admin property. By default, the administrator is the user who created the metastore, but it's best practice to delegate administative capabilities to a group, so let's now change this to the *metastore_admins* group.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Deleting a metastore
# MAGIC
# MAGIC When metastores are no longer needed, we can delete them using the account console.
# MAGIC
# MAGIC 1. In the **Data** page, let's select the desired metastore.
# MAGIC 1. Click **Delete**.
# MAGIC 1. As this is a fairly destructive operation, we will need to confirm before proceeding. For now, let's cancel.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Workspaces
# MAGIC
# MAGIC A Databricks workspace is an environment for accessing all of your Databricks assets. The workspace organizes objects (notebooks, libraries, and experiments) into folders, integrates revision control, and provides access to data and computational resources such as clusters and jobs. A workspace also provides access to Databricks SQL, a simple experience for SQL users who want to query, explore and visualize queries on their data lake.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a workspace
# MAGIC
# MAGIC With all the supporting resources in place, we are now ready to create a workspace.
# MAGIC
# MAGIC 1. In the account console, let's click on the **Workspaces** icon in the left sidebar. This will display a list of currently created workspaces.
# MAGIC 1. Let's click **Create workspace**.
# MAGIC 1. Let's provide the **Workspace name**. This will have user visibility (let's use *dbacademy-test-workspace* for this example).
# MAGIC 1. Let's fill out the **Workspace URL**. If left blank, the system will choose a name though it may not be as human-readable. In this case, let's repeat the value we specified for the name.
# MAGIC 1. Let's choose the region that matches the region in which we created the root storage bucket.
# MAGIC 1. Let's choose the credential configuration and storage configuration we created previously.
# MAGIC 1. Ensure that **Unity Catalog** is enabled. This feature allows the workspace to be integrated with a Unity Catalog metastore, as well as the account console for identity federation.
# MAGIC 1. Let's choose the metastore we created previously. This can be swapped out at any time as needed.
# MAGIC 1. Finally, let's click **Save**.
# MAGIC
# MAGIC The workspace will take a few moments to provision. Once complete, the platform will issue a notication to the email address of the user who created the workspace. That same user will automatically be assigned as a workspace admin.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Deleting a workspace
# MAGIC
# MAGIC When workspaces are no longer needed, we can delete them using the account console.
# MAGIC
# MAGIC 1. In the **Workspaces** page, let's locate the desired workspace (using the **Search** field, if desired).
# MAGIC 1. Click the three dots in the rightmost column.
# MAGIC 1. Select **Delete**.
# MAGIC 1. As this is a fairly destructive operation, we will need to confirm before proceeding. For now, let's cancel.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Assigning a metastore
# MAGIC
# MAGIC In order to use a metastore, it must be assigned to a workspace. A metastore can be assigned to multiple workspaces, though any given workspace can only have one metastore assigned to it at any given time, and the metastore and workspace must reside in the same region.
# MAGIC
# MAGIC 1. In the **Data** page of the account console, let's choose the metastore we want to assign.
# MAGIC 1. Let's click the **Workspaces** tab. This displays a list of workspaces to which the metastore is currently assigned.
# MAGIC 1. Let's click **Assign to workspace**.
# MAGIC 1. Let's select the desired workspace (more can be chosen, if desired).
# MAGIC 1. Finally, we click **Assign**.
# MAGIC
# MAGIC We can detach the metastore from any currently assigned workspace.
# MAGIC
# MAGIC 1. In the **Data** page of the account console, let's choose the metastore we want to detach.
# MAGIC 1. Let's click the **Workspaces** tab. This displays a list of workspaces to which the metastore is currently assigned.
# MAGIC 1. Let's click the three dots at the far right side of the row representing the workspace.
# MAGIC 1. Let's select **Remove from this metastore**.
# MAGIC
# MAGIC Warning: when reassigning metastores, be mindful of the impact this could have on scheduled or running jobs.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2023 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="https://help.databricks.com/">Support</a>
