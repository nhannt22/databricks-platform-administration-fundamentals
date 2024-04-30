# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Deploying a workspace in a customer-managed VPC
# MAGIC
# MAGIC In this lab you will learn how to:
# MAGIC * Create your own VPC
# MAGIC * Integrate your VPC into the Databricks account console
# MAGIC * Create new workspaces using that VPC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prerequisites
# MAGIC
# MAGIC If you would like to follow along with this lab, you will need:
# MAGIC * administrator access to your AWS console, with the ability to create VPCs, buckets and IAM roles
# MAGIC * account administrator capabilities in your Databricks account in order to access the account console
# MAGIC * performing the *Supporting Databricks workspaces and metastores* lab from the *AWS Databricks Platform Administration Fundamentals* course will be a benefit, as this lab is largely an extension of that one

# COMMAND ----------

# MAGIC %md
# MAGIC ## Supporting a workspace in a custom VPC
# MAGIC
# MAGIC You will recall from the *Supporting Databricks workspaces and metastores* lab from the *AWS Databricks Platform Administration Fundamentals* course, we created the AWS and Databricks elements needed to support the creation of a Databricks workspace using the default VPC configuration. In this lab, we'll work through a modified approach that enable us to have full control of the VPC. While some of this may seem familiar, there are differences to accomodate for the custom VPC.
# MAGIC
# MAGIC With that said, let's proceed.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a VPC
# MAGIC
# MAGIC The first thing we need in this scenario is a VPC. In the *Supporting Databricks workspaces and metastores* lab, we allowed Databricks to manage this aspect for us, but here we must create and configure a suitable VPC for workspace deployment.
# MAGIC
# MAGIC 1. In the AWS VPC console, let's select the region in which we're deploying our workspaces; let's use *us-east-1*.
# MAGIC 1. Click **Create VPC**.
# MAGIC 1. Let's select **VPC and more**.
# MAGIC 1. Let's specify a value for **Name tag auto-generation**. Databricks recommends including the region in the name. Let's use *dbacademy-test-vpc-us-east-1*.
# MAGIC 1. Let's leave the IPv4 and IPv6 CIDR block settings as they are, though we could modify these if needed.
# MAGIC 1. Select *2* for the nubmer of public subnets. Databricks doesn't need them both, but they are required to enable NATs.
# MAGIC 1. Select *2* for the number of private subnets. Each workspace needs two, so two will be sufficient to get started with one workspace.
# MAGIC 1. Select *In 1 AZ* for **NAT gateways**.
# MAGIC 1. Ensure that both **Enable DNS hostnames** and **Enable DNS resolution** are enabled.
# MAGIC 1. Finally, let's click **Create VPC**. 
# MAGIC
# MAGIC This will trigger the creation of the VPC and all related resources, and will take a few moments to complete. Once done, you can proceed.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Configuring the VPC
# MAGIC
# MAGIC Databricks has some requirements for its VPCs at outlined in the <a href="https://docs.databricks.com/administration-guide/cloud-configurations/aws/customer-managed-vpc.html#vpc-requirements-1" target="_blank">documentation</a>. Though the default parameters will work for Databricks workspaces, you'll likely want to reconfigure various aspects of your VPC at some point.
# MAGIC
# MAGIC In the **VPC Management Console** let's use the filter functionality to isolate items related to the VPC we created. From here we can review or configure elements related to the VPC, which we will do shortly. For now, let's proceed to create a workspace using this VPC.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a cross-account IAM role
# MAGIC
# MAGIC In this section, we'll create the cross-acount role. Rather than using the one we created in the *Supporting Databricks workspaces and metastores* lab, we'll create a new one with fewer permissions, since we do not need to allow Databricks to manage VPCs or their associated resources. The policy we use here is a watered-down version of the policy needed when using Databricks default VPCs. This policy does not allow Databricks to manage VPCs or the associated resources like addresses, routes and tables, subnets, gateways, and security groups.
# MAGIC
# MAGIC 1. In the AWS IAM console, let's select **Roles**.
# MAGIC 1. Click **Create role**.
# MAGIC 1. Select **AWS account**. This will let us set up a cross-account trust relationship that will allow Databricks to provision resources in our account.
# MAGIC    * Select **Another AWS account**.
# MAGIC    * For **Account ID**, let's substitute in the Databricks account ID, *414351767826*.
# MAGIC    * Select **Require external ID**.
# MAGIC    * For **External ID**, let's paste our Databricks account ID. We can easily get this from the user menu in the account console.
# MAGIC    * Now let's click **Next** until we get to the final page.
# MAGIC    * Let's assign the name for our role (use *dbacademy-test-cross-account-role-novpc*).
# MAGIC    * Click **Create role**.
# MAGIC 1. Now let's view the role we just created.
# MAGIC 1. Let's click the **Permissions** tab.
# MAGIC 1. Let's select **Add permissions > Create inline policy**.
# MAGIC 1. Click the **JSON** tab.
# MAGIC 1. Replace the default policy with the following:
# MAGIC     ```
# MAGIC     {
# MAGIC       "Version": "2012-10-17",
# MAGIC       "Statement": [
# MAGIC         {
# MAGIC           "Sid": "Stmt1403287045000",
# MAGIC           "Effect": "Allow",
# MAGIC           "Action": [
# MAGIC             "ec2:AssociateIamInstanceProfile",
# MAGIC             "ec2:AttachVolume",
# MAGIC             "ec2:AuthorizeSecurityGroupEgress",
# MAGIC             "ec2:AuthorizeSecurityGroupIngress",
# MAGIC             "ec2:CancelSpotInstanceRequests",
# MAGIC             "ec2:CreateTags",
# MAGIC             "ec2:CreateVolume",
# MAGIC             "ec2:DeleteTags",
# MAGIC             "ec2:DeleteVolume",
# MAGIC             "ec2:DescribeAvailabilityZones",
# MAGIC             "ec2:DescribeIamInstanceProfileAssociations",
# MAGIC             "ec2:DescribeInstanceStatus",
# MAGIC             "ec2:DescribeInstances",
# MAGIC             "ec2:DescribeInternetGateways",
# MAGIC             "ec2:DescribeNatGateways",
# MAGIC             "ec2:DescribeNetworkAcls",
# MAGIC             "ec2:DescribePrefixLists",
# MAGIC             "ec2:DescribeReservedInstancesOfferings",
# MAGIC             "ec2:DescribeRouteTables",
# MAGIC             "ec2:DescribeSecurityGroups",
# MAGIC             "ec2:DescribeSpotInstanceRequests",
# MAGIC             "ec2:DescribeSpotPriceHistory",
# MAGIC             "ec2:DescribeSubnets",
# MAGIC             "ec2:DescribeVolumes",
# MAGIC             "ec2:DescribeVpcAttribute",
# MAGIC             "ec2:DescribeVpcs",
# MAGIC             "ec2:DetachInternetGateway",
# MAGIC             "ec2:DetachVolume",
# MAGIC             "ec2:DisassociateIamInstanceProfile",
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
# MAGIC 1. Let's assign the name for our policy (use *dbacademy-test-cross-account-policy-novpc*).
# MAGIC 1. Click **Create policy**.
# MAGIC 1. Let's take note of the **ARN**; the account administrator will need this in order to create a credential configuration that captures this IAM role.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating the workspace root storage bucket
# MAGIC
# MAGIC As we did in the *Supporting Databricks workspaces and metastore* lab, let's create an S3 bucket to function as the workspace root storage.
# MAGIC
# MAGIC 1. In the AWS S3 console, click **Create bucket**.
# MAGIC 1. Let's specify a name. When choosing your own names, be mindful to not include dots in your names (use *dbacademy-test-workspace-bucket-novpc*).
# MAGIC 1. Let's choose the region where we created the VPC.
# MAGIC 1. For this example, let's accept the default settings for the rest, and create the bucket. We will need to revisit it in a moment to add a policy.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating Databricks cloud resources
# MAGIC
# MAGIC With everything created on the AWS side, let's go to the Databricks account console to create the resources needed to set up a new workspace.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating the credential configuration
# MAGIC
# MAGIC If you'll recall, the credential configuration is the piece that encapsulates the cross account IAM role. As we did in the *Supporting Databricks workspaces and metastores* lab, let's create a credential configuration for the cross-account IAM role we just created.
# MAGIC
# MAGIC 1. In the account console, let's click on the **Cloud Resources** icon in the left sidebar.
# MAGIC 1. Let's click the **Credential configuration** tab.
# MAGIC 1. Let's click **Add credential configuration**.
# MAGIC 1. Let's provide a name for the configuration. This name will have no user visibility (use *dbacademy-test-credential-configuration-novpc*).
# MAGIC 1. Paste the **ARN** for the role we created moments ago.
# MAGIC 1. Finally, let's click **Add**.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating a storage configuration
# MAGIC
# MAGIC If you'll recall, the storage configuration is the piece that encapsulates the S3 bucket that will store workspace-related objects. Let's create that now.
# MAGIC
# MAGIC 1. Still in the **Cloud Resources** page, let's click the **Storage configuration** tab.
# MAGIC 1. Let's click **Add storage configuration**.
# MAGIC 1. Let's provide a name for the configuration. This name will have no user visibility (use *dbacademy-test-storage-configuration-novpc*).
# MAGIC 1. Let's enter the name for the bucket we created moments ago (*dbacademy-test-workspace-bucket-novpc*).
# MAGIC 1. Now we need to add a policy to that bucket. Let's click the **Generate policy** link and copy the JSON policy description.
# MAGIC 1. Finally, let's click **Add**.
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
# MAGIC ### Creating the network configuration
# MAGIC
# MAGIC The network configuration encapsulates the VPC and subnets which the workspace will use. In order to create this we will need, at a minimum, the following pieces of information related to the VPC we created earler:
# MAGIC * the VPC ID
# MAGIC * the IDs of the two private subnets
# MAGIC * the security group ID
# MAGIC
# MAGIC Let's obtain that information now.
# MAGIC
# MAGIC 1. In the VPC Management Console let's filter on our VPC.
# MAGIC 1. Let's take note of the VPC ID.
# MAGIC 1. Select **Subnets**. The 4 subnets related to our VPC are displayed. Two of these are public and two are private; we are primarily interested in the private ones for now, which can be identified by their names. Let's take note of the Subnet IDs for both.
# MAGIC 1. Finally, let's select **Security groups** and take note of the Security group ID.
# MAGIC
# MAGIC Let's return to the **Cloud Resources** page of the account console.
# MAGIC
# MAGIC 1. In the **Network** tab, let's click **Add network configuration**.
# MAGIC 1. Let's provide a name for the configuration. This name will have no user visibility (use *dbacademy-test-network-configuration-ws1*).
# MAGIC 1. Supply the values we gathered for **VPC ID**, **Subnet IDs** and **Security group IDs**.
# MAGIC 1. Finally, let's click **Add**.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a workspace
# MAGIC
# MAGIC With all the supporting resources in place, we are now ready to create a workspace.
# MAGIC
# MAGIC 1. In the account console, let's click on the **Workspaces** icon in the left sidebar.
# MAGIC 1. Let's click **Create workspace**.
# MAGIC 1. Let's provide the **Workspace name** (let's use *dbacademy-test-workspace-ws1* for this example).
# MAGIC 1. Let's fill out the **Workspace URL**.
# MAGIC 1. Let's choose the region that matches the region in which we created the other resources.
# MAGIC 1. Let's choose the credential configuration and storage configuration we created previously.
# MAGIC 1. Let's leave **Unity Catalog** disabled. The VPC configuration in this example does not impact the procedure for creating and setting up a metastore, which we did in the *Supporting Databricks workspaces and metastores* lab.
# MAGIC 1. Let's open **Advanced configurations**.
# MAGIC 1. For **Network configuration**, let's select the network configuration we created earlier.
# MAGIC 1. Finally, let's click **Save**.
# MAGIC
# MAGIC The workspace will take a few moments to provision. Apart from completing faster, there will no apparent difference. But remember that in this scenario, the Databricks control plane is creating the workspace under a significantly reduced set of permissions, using a VPC that we created ourselves.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating additional workspaces
# MAGIC
# MAGIC Housing multiple workspaces is a common use case for customer-managed VPCs. But it's important to note that each workspace requires two private subnets that cannot be shared. Because of this, we must:
# MAGIC * Create two additional subnets in our VPC
# MAGIC * Create a new network configuration (since the account console will not allow a second workspace to be created using the same network configuration)
# MAGIC
# MAGIC Before we proceed, note the following constraints:
# MAGIC * The subnets must be private (that is, IP addresses are private, with routing to the outside provided via a NAT)
# MAGIC * The subnets must be assigned an address block that doesn't overlap with any other subnets in the VPC
# MAGIC * The two must be in different availability zones
# MAGIC * Both must have a routing to the outside using the VPC's NAT
# MAGIC
# MAGIC Let's do this now.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating subnets
# MAGIC
# MAGIC Let's go ahead and create the subnets.
# MAGIC
# MAGIC 1. In the **VPC Management Console** let's filter on our VPC.
# MAGIC 1. Now let's select **Subnets**. Note the IPv4 CIDR blocks of the existing subnets, for we must create two new subnets that do not overlap. Based on the standard configuration offered by the VPC wizard, *10.0.160.0/20* and *10.0.176.0/20* are available.
# MAGIC 1. Let's click **Create subnet**.
# MAGIC 1. Let's select our VPC, *dbacademy-test-vpc-us-east-1-vpc*.
# MAGIC 1. Let's specify a name. If we wish, we can adopt the convention used by the VPC creation wizard, or we can use a simpler approach. For the purpose of this exercise, let's simply use *my-subnet-01*.
# MAGIC 1. Let's select *us-east-1a* for the **Availability Zone**.
# MAGIC 1. Let's specify *10.0.160.0/20* for the **IPv4 CIDR block**.
# MAGIC 1. Now let's click **Add new subnet** to fill in information for the second subnet:
# MAGIC    * *my-subnet-02* for the name
# MAGIC    * *us-east-1b* for the **Availability Zone**
# MAGIC    * *10.0.176.0/20* for the **IPv4 CIDR block**
# MAGIC 1. Finally, let's click **Create subnet**.

# COMMAND ----------

# MAGIC %md
# MAGIC #### Creating route tables
# MAGIC
# MAGIC The two subnets we created will by default be associated with the VPC's default route table. However this route table lacks the needed routing to the outside world to communicate
# MAGIC
# MAGIC According to the <a href="https://docs.databricks.com/administration-guide/cloud-configurations/aws/customer-managed-vpc.html#subnets" target="_blank">documentation</a>, the route table for workspace subnets must have quad-zero (0.0.0.0/0) traffic that targets a NAT Gateway or your own managed NAT device or proxy appliance.
# MAGIC
# MAGIC Let's set up a new route table that will accomplish this now.
# MAGIC
# MAGIC 1. In the **VPC Management Console** let's select **Route tables**.
# MAGIC 1. Let's click **Create route table**.
# MAGIC 1. Let's specify a name. Once again, we can keep the naming simple by choosing a name like *my-route-table-01*.
# MAGIC 1. Let's select our VPC, *dbacademy-test-vpc-us-east-1-vpc*.
# MAGIC 1. Let's click **Create route table**.
# MAGIC 1. With the newly create table display, let's click **Edit routes**.
# MAGIC 1. Now let's click **Add route**.
# MAGIC 1. Specify *0.0.0.0/0* for the **Destination**.
# MAGIC 1. For the **Target**, let's select *NAT gateway*. This will present the one and only NAT gateway available in the VPC, so let's choose that.
# MAGIC 1. Let's click **Save changes**.
# MAGIC
# MAGIC With a route table configured let's associate that with one of our subnets.
# MAGIC
# MAGIC 1. In the **VPC Management Console** let's select **Subnets**.
# MAGIC 1. Let's locate and select the first subnet we created (*my-subnet-01*).
# MAGIC 1. Select **Actions > Edit route table association**.
# MAGIC 1. Select the route table we just created (*my-route-table-01*) and then click **Save**.
# MAGIC
# MAGIC Now, let's repeat this process once more to create a similarly configured second route table, *my-route-table-02*, and associated that with *my-subnet-02*.

# COMMAND ----------

# MAGIC %md
# MAGIC Before proceeding, let's take note of the two new subnet IDs that we will need to create a new network configuration. The VPC and security group IDs remain unchanged from before.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating a new network configuration
# MAGIC
# MAGIC Let's return to the **Cloud Resources** page of the account console to create a new network configuration encapsulating our new subnets.
# MAGIC
# MAGIC 1. In the **Network** tab, let's click **Add network configuration**.
# MAGIC 1. Let's provide a name for the configuration (use *dbacademy-test-network-configuration-ws2*).
# MAGIC 1. Supply the values for **VPC ID**, the **Subnet IDs** for the two subnets we just created, and **Security group IDs**.
# MAGIC 1. Finally, let's click **Add**.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating a second workspace
# MAGIC
# MAGIC Finally, let's create a new workspace.
# MAGIC
# MAGIC 1. In the account console, let's click on the **Workspaces** icon in the left sidebar.
# MAGIC 1. Let's click **Create workspace**.
# MAGIC 1. Let's provide the **Workspace name** (let's use *dbacademy-test-workspace-ws2* for this example).
# MAGIC 1. Let's fill out the **Workspace URL**.
# MAGIC 1. Let's choose the region that matches the region in which we created the other resources.
# MAGIC 1. Let's choose the credential configuration and storage configuration we used for the previous workspace.
# MAGIC 1. As before, let's leave **Unity Catalog** disabled.
# MAGIC 1. Let's open **Advanced configurations** and select the new network configuration.
# MAGIC 1. Finally, let's click **Save**.
# MAGIC
# MAGIC Once again, there will no apparent difference, but now the two workspaces will be sharing a VPC, its configuration, and all AWS resources within it. The ability to architect your Databricks setup in this way provides a significant amount of flexibility.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2023 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="https://help.databricks.com/">Support</a>
