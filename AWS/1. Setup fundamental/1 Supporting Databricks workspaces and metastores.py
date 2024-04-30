# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Supporting Databricks workspaces and metastores
# MAGIC
# MAGIC In this lab you will learn how to:
# MAGIC * Create AWS resources needed to support a Databricks workspace
# MAGIC * Create AWS resources needed to support a Unity Catalog metastore
# MAGIC * Create cloud resources to bring awareness of these AWS resources to Databricks

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prerequisites
# MAGIC
# MAGIC If you would like to follow along with this lab, you will need:
# MAGIC * administrator access to your AWS console, with the ability to create buckets and IAM roles
# MAGIC * account administrator capabilities in your Databricks account in order to access the account console

# COMMAND ----------

# MAGIC %md
# MAGIC ## Supporting a workspace
# MAGIC
# MAGIC A Databricks workspace is an environment for accessing all of your Databricks assets. The workspace organizes objects (notebooks, libraries, and experiments) into folders, integrates revision control, and provides access to data and computational resources such as clusters and jobs. A workspace also provides access to Databricks SQL, a simple experience for SQL users who want to query, explore and visualize queries on their data lake.
# MAGIC
# MAGIC There are some underlying AWS resources that must be set up first in order to support the workspace. These include:
# MAGIC * A cross-account credential that allows Databricks to launch clusters in the account (in AWS, this means an IAM role)
# MAGIC * An S3 bucket to provide workspace root storage. This will require a specialized policy to permit Databricks to access the bucket.
# MAGIC
# MAGIC We will create these elements in this demo, however note that this procedure is also documented <a href="https://docs.databricks.com/administration-guide/account-settings-e2/workspaces.html" target="_blank">here</a>. We will be referencing this documentation throughout the demo.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating a credential configuration
# MAGIC
# MAGIC In order for the software running in the Databricks control plane to create and manage compute resources like clusters and VPCs within your account, limited access to your AWS account is required, which is enabled through a cross account IAM role. In this section, we'll create and appropriately configure such a credential, then wrap it into a credential configuration that can be used by Databricks when deploying a workpace.

# COMMAND ----------

# MAGIC %md
# MAGIC #### Creating a cross-account IAM role
# MAGIC
# MAGIC In this section, we'll create and appropriately configure cross-account IAM role to allow Databricks to create and manage VPCs and cluster in your own AWS account. Note that the policy we use applies to the default Databricks-managed VPC. A different policy is needed if providing your own VPC; we talk about this in a separate course.
# MAGIC
# MAGIC 1. In the AWS IAM console, let's select **Roles**.
# MAGIC 1. Click **Create role**.
# MAGIC 1. Select **AWS account**. This will let us set up a cross-account trust relationship that will allow Databricks, running in its own account, to assume the role to access services in our account.
# MAGIC    * Select **Another AWS account**.
# MAGIC    * For **Account ID**, let's substitute in the Databricks account ID, *414351767826*.
# MAGIC    * Select **Require external ID**.
# MAGIC    * For **External ID**, let's paste our Databricks account ID. We can easily get this from the user menu in the account console.
# MAGIC    * Now let's click **Next** until we get to the final page.
# MAGIC    * Let's assign the name for our role (use *dbacademy-test-cross-account-role*).
# MAGIC    * Click **Create role**.
# MAGIC 1. Now let's view the role we just created.
# MAGIC 1. In the **Permissions** tab, let's select **Add permissions > Create inline policy**.
# MAGIC 1. In the **JSON** tab, replace the default policy with the following:
# MAGIC     ```
# MAGIC     {
# MAGIC       "Version": "2012-10-17",
# MAGIC       "Statement": [
# MAGIC         {
# MAGIC           "Sid": "Stmt1403287045000",
# MAGIC           "Effect": "Allow",
# MAGIC           "Action": [
# MAGIC             "ec2:AllocateAddress",
# MAGIC             "ec2:AssociateDhcpOptions",
# MAGIC             "ec2:AssociateIamInstanceProfile",
# MAGIC             "ec2:AssociateRouteTable",
# MAGIC             "ec2:AttachInternetGateway",
# MAGIC             "ec2:AttachVolume",
# MAGIC             "ec2:AuthorizeSecurityGroupEgress",
# MAGIC             "ec2:AuthorizeSecurityGroupIngress",
# MAGIC             "ec2:CancelSpotInstanceRequests",
# MAGIC             "ec2:CreateDhcpOptions",
# MAGIC             "ec2:CreateInternetGateway",
# MAGIC             "ec2:CreateNatGateway",
# MAGIC             "ec2:CreateRoute",
# MAGIC             "ec2:CreateRouteTable",
# MAGIC             "ec2:CreateSecurityGroup",
# MAGIC             "ec2:CreateSubnet",
# MAGIC             "ec2:CreateTags",
# MAGIC             "ec2:CreateVolume",
# MAGIC             "ec2:CreateVpc",
# MAGIC             "ec2:CreateVpcEndpoint",
# MAGIC             "ec2:DeleteDhcpOptions",
# MAGIC             "ec2:DeleteInternetGateway",
# MAGIC             "ec2:DeleteNatGateway",
# MAGIC             "ec2:DeleteRoute",
# MAGIC             "ec2:DeleteRouteTable",
# MAGIC             "ec2:DeleteSecurityGroup",
# MAGIC             "ec2:DeleteSubnet",
# MAGIC             "ec2:DeleteTags",
# MAGIC             "ec2:DeleteVolume",
# MAGIC             "ec2:DeleteVpc",
# MAGIC             "ec2:DeleteVpcEndpoints",
# MAGIC             "ec2:DescribeAvailabilityZones",
# MAGIC             "ec2:DescribeIamInstanceProfileAssociations",
# MAGIC             "ec2:DescribeInstanceStatus",
# MAGIC             "ec2:DescribeInstances",
# MAGIC             "ec2:DescribeInternetGateways",
# MAGIC             "ec2:DescribeNatGateways",
# MAGIC             "ec2:DescribePrefixLists",
# MAGIC             "ec2:DescribeReservedInstancesOfferings",
# MAGIC             "ec2:DescribeRouteTables",
# MAGIC             "ec2:DescribeSecurityGroups",
# MAGIC             "ec2:DescribeSpotInstanceRequests",
# MAGIC             "ec2:DescribeSpotPriceHistory",
# MAGIC             "ec2:DescribeSubnets",
# MAGIC             "ec2:DescribeVolumes",
# MAGIC             "ec2:DescribeVpcs",
# MAGIC             "ec2:DetachInternetGateway",
# MAGIC             "ec2:DisassociateIamInstanceProfile",
# MAGIC             "ec2:DisassociateRouteTable",
# MAGIC             "ec2:ModifyVpcAttribute",
# MAGIC             "ec2:ReleaseAddress",
# MAGIC             "ec2:ReplaceIamInstanceProfileAssociation",
# MAGIC             "ec2:RequestSpotInstances",
# MAGIC             "ec2:RevokeSecurityGroupEgress",
# MAGIC             "ec2:RevokeSecurityGroupIngress",
# MAGIC             "ec2:RunInstances",
# MAGIC             "ec2:TerminateInstances"
# MAGIC           ],
# MAGIC           "Resource": [
# MAGIC             "*"
# MAGIC           ]
# MAGIC         },
# MAGIC         {
# MAGIC           "Effect": "Allow",
# MAGIC           "Action": [
# MAGIC               "iam:CreateServiceLinkedRole",
# MAGIC               "iam:PutRolePolicy"
# MAGIC           ],
# MAGIC           "Resource": "arn:aws:iam::*:role/aws-service-role/spot.amazonaws.com/AWSServiceRoleForEC2Spot",
# MAGIC           "Condition": {
# MAGIC             "StringLike": {
# MAGIC                 "iam:AWSServiceName": "spot.amazonaws.com"
# MAGIC             }
# MAGIC           }
# MAGIC         }
# MAGIC       ]
# MAGIC     }
# MAGIC     ```
# MAGIC 1. Now let's click **Review policy** to get to the final page.
# MAGIC 1. Let's assign the name for our policy (use *dbacademy-test-cross-account-policy*).
# MAGIC 1. Click **Create policy**.
# MAGIC 1. Let's take note of the **ARN**; the account administrator will need this in order to create a credential configuration that captures this IAM role.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating the credential configuration
# MAGIC
# MAGIC With a cross account IAM role create, we need a way to represent that in Databricks. For this reason, we have *credential configurations*, which we create in this section using the account console.
# MAGIC
# MAGIC 1. In the account console, let's click on the **Cloud Resources** icon in the left sidebar.
# MAGIC 1. Let's click the **Credential configuration** tab.
# MAGIC 1. Let's click **Add credential configuration**.
# MAGIC 1. Let's provide a name for the configuration. This name will have no user visibility (use *dbacademy-test-credential-configuration*).
# MAGIC 1. Paste the **ARN** for the role we created moments ago.
# MAGIC 1. Finally, let's click **Add**.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating a storage configuration
# MAGIC
# MAGIC Workspaces need an S3 bucket collocated in the same region to store objects that are generated as the platform is used. These stored objects include:
# MAGIC * Cluster logs
# MAGIC * Notebook revisions
# MAGIC * Job results
# MAGIC * Libraries
# MAGIC * Any files written to the DBFS root, either by a job or uploaded from the user interface
# MAGIC * Tables written to the legacy metastore
# MAGIC
# MAGIC With an appropriately configured bucket in place, we then need to create a *storage configuration* in the account console to represent this bucket.
# MAGIC
# MAGIC Note that you can share a bucket between more than one workspace, though Databricks advises against this.

# COMMAND ----------

# MAGIC %md
# MAGIC #### Creating the workspace root storage bucket
# MAGIC
# MAGIC Let's create an S3 bucket to function as the workspace root storage.
# MAGIC
# MAGIC 1. In the AWS S3 console, let's click **Create bucket**.
# MAGIC 1. Let's specify a name. When choosing your own names, be mindful to not include dots in your names. Bucket names must also be globally unique. In this example we use *dbacademy-test-workspace-bucket*, but you should include a suffix or prefix that uniquely ties the name to your organization; for example, replace *dbacademy* with your domain name (using hyphens instead of dots).
# MAGIC 1. Let's choose the region where we plan on creating our workspace.
# MAGIC 1. For this example, let's accept the default settings for the rest, and create the bucket. We will need to revisit it in a moment to add a policy.

# COMMAND ----------

# MAGIC %md
# MAGIC #### Creating a storage configuration
# MAGIC
# MAGIC Now let's create the piece that links Databricks to the storage container for the workspace we will create.
# MAGIC 1. In the account console, let's click on the **Cloud Resources** icon in the left sidebar.
# MAGIC 1. Let's click the **Storage configuration** tab.
# MAGIC 1. Let's click **Add storage configuration**.
# MAGIC 1. Let's provide a name for the configuration. This name will have no user visibility (use *dbacademy-test-storage-configuration*).
# MAGIC 1. Let's enter the name for the bucket we created moments ago (*dbacademy-test-workspace-bucket*).
# MAGIC 1. Now we need to add a policy to that bucket. Let's click the **Generate policy** link and copy the JSON policy description.
# MAGIC 1. Finally, let's click **Add**.

# COMMAND ----------

# MAGIC %md
# MAGIC #### Adding the policy to the bucket
# MAGIC
# MAGIC With a policy on the clipboard, let's revisit the S3 console to add that policy to the bucket we created earlier.
# MAGIC
# MAGIC 1. In the AWS S3 console, let's find the bucket we created and select it.
# MAGIC 1. Let's click the **Permissions** tab.
# MAGIC 1. In the **Bucket policy** area, click **Edit**.
# MAGIC 1. Let's paste the JSON policy.
# MAGIC 1. Finally, let's click **Save changes**.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Supporting a metastore
# MAGIC
# MAGIC A metastore is the top-level container of data objects in Unity Catalog. The metastore contains metadata about your tables and, in the case of managed tables, the table data itself. 
# MAGIC
# MAGIC Account administrators create metastores and assign them to workspaces to allow workloads in those workspaces to access the data represented in the metastore. This can be done in the account console, through REST APIs, or using <a href="https://registry.terraform.io/providers/databrickSlabs/databricks/latest/docs" target="_blank">Terraform</a>. In this demo, we will explore the creation and management of metastores interactively using the account console.
# MAGIC
# MAGIC There are some underlying cloud resources that must be set up first in order to support the metastore. This includes:
# MAGIC * An S3 bucket for storing metastore artifacts located in your own AWS account
# MAGIC * An IAM role that allows Databricks to access the bucket
# MAGIC
# MAGIC We will create these elements in this demo, but note that this procedure is also documented <a href="https://docs.databricks.com/data-governance/unity-catalog/get-started.html#configure-aws-objects" target="_blank">here</a>. We will be referencing this documentation throughout the demo.
# MAGIC
# MAGIC It's important to keep the following constraints in mind when creating and managing metastores:
# MAGIC * You can create only one metastore per region
# MAGIC * Metastores can only be associated with workspaces in the same region
# MAGIC * There can be as many workspaces as needed associated with a metastore located within the same region.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating the metastore bucket
# MAGIC
# MAGIC Databricks recommends creating a dedicated bucket for each metastore. We do not recommended sharing this bucket for any other purpose than hosting the metastore. Here we will create a bucket named *dbacademy-test-metastore-bucket* for this purpose. 
# MAGIC
# MAGIC 1. Still in the AWS S3 console, let's click **Create bucket**.
# MAGIC 1. Let's specify our name. Once again, be mindful to not include dots in your names, and that names must be globally unique. For this example we use *dbacademy-test-metastore-bucket*, but adjust your name accordingly.
# MAGIC 1. Let's choose a region that matches with the workspace bucket we created earlier.
# MAGIC 1. For this example, let's accept the default settings for the rest, and create the bucket.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating an IAM policy
# MAGIC
# MAGIC Before creating the IAM role that Unity Catalog needs, we need to create a policy that defines how this bucket can be accessed. This must be done using the same AWS account as the bucket.
# MAGIC
# MAGIC 1. In the AWS IAM console, let's select **Policies**.
# MAGIC 1. Click **Create policy**.
# MAGIC 1. Let's select the **JSON** tab and replace the default policy with the following, which we use as a starting point:
# MAGIC     ```
# MAGIC     {
# MAGIC      "Version": "2012-10-17",
# MAGIC      "Statement": [
# MAGIC          {
# MAGIC              "Action": [
# MAGIC                  "s3:GetObject",
# MAGIC                  "s3:PutObject",
# MAGIC                  "s3:DeleteObject",
# MAGIC                  "s3:ListBucket",
# MAGIC                  "s3:GetBucketLocation",
# MAGIC                  "s3:GetLifecycleConfiguration",
# MAGIC                  "s3:PutLifecycleConfiguration"
# MAGIC              ],
# MAGIC              "Resource": [
# MAGIC                  "arn:aws:s3:::<BUCKET>/*",
# MAGIC                  "arn:aws:s3:::<BUCKET>"
# MAGIC              ],
# MAGIC              "Effect": "Allow"
# MAGIC          },
# MAGIC          {
# MAGIC              "Action": [
# MAGIC                  "sts:AssumeRole"
# MAGIC              ],
# MAGIC              "Resource": [
# MAGIC                  "arn:aws:iam::<AWS_ACCOUNT_ID>:role/<AWS_IAM_ROLE_NAME>"
# MAGIC              ],
# MAGIC              "Effect": "Allow"
# MAGIC          }
# MAGIC        ]
# MAGIC     }
# MAGIC     ```
# MAGIC 1. Now let's customize the policy.
# MAGIC    * Replace instances of **`<BUCKET>`** with the name of the bucket we created.
# MAGIC    * Replace **`<AWS_ACCOUNT_ID>`** with the account ID of the current AWS account, which is accessible from the user menu in the AWS console.
# MAGIC    * Replace **`<AWS_IAM_ROLE_NAME>`** with the name of the IAM role that we will create, *dbacademy-test-metastore-role*.
# MAGIC 1. Let's click through accepting the default settings for the rest and specifying a suitable name (use *dbacademy-test-metastore-policy*), then create the policy.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating an IAM role
# MAGIC
# MAGIC Let's create an IAM role that will allow Databricks to access this bucket residing in your own account.
# MAGIC 1. In the AWS console, let's go to **IAM > Roles**.
# MAGIC 1. Click **Create role**.
# MAGIC 1. Select **Custom trust policy**. This will let us set up a cross-account trust relationship that will allow Unity Catalog to assume the role to acccess the bucket on our behalf.
# MAGIC    * In the **Custom trust policy** area, let's paste the following policy as a starting point.
# MAGIC     ```
# MAGIC     {
# MAGIC       "Version": "2012-10-17",
# MAGIC       "Statement": [
# MAGIC         {
# MAGIC           "Effect": "Allow",
# MAGIC           "Principal": {
# MAGIC             "AWS": "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL"
# MAGIC           },
# MAGIC           "Action": "sts:AssumeRole",
# MAGIC           "Condition": {
# MAGIC             "StringEquals": {
# MAGIC               "sts:ExternalId": "<DATABRICKS_ACCOUNT_ID>"
# MAGIC             }
# MAGIC           }
# MAGIC         }
# MAGIC       ]
# MAGIC     }
# MAGIC     ```
# MAGIC    * For **`<DATABRICKS_ACCOUNT_ID>`** let's substitute in our Databricks account ID. We can easily get this from the account console as we did earlier. Treat this value carefully like you would any other credential.
# MAGIC    * Now let's click **Next**.
# MAGIC 1. Now let's locate and select the policy we created.
# MAGIC 1. Finally, let's assign the name for our role. Let's use *dbacademy-test-metastore-role* and create the role.
# MAGIC 1. Let's take note of the **ARN** as the account administrator will need this when creating the metastore.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2023 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="https://help.databricks.com/">Support</a>
