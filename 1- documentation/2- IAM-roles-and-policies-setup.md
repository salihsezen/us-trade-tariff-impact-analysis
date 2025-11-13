> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 2- IAM-roles-and-policies-setup.md


# IAM Roles and Policies Setup  

This document lists the **IAM roles** used in the project, explains what they do, and summarizes their key policies and trust relationships.

## Notes & Best Practices

Do not attach Admin policies to service roles for this project.
Scope S3 ARNs and actions as tightly as possible.
If you add new buckets or prefixes later, update the S3 Resource list in these policies accordingly.
I am only granting FullAccess permissions so that I can quickly run the services in the project without encountering authorization issues. In real-world scenarios, read-only permissions and a more or less permission policy would be sufficient.
---

## 1. Overview of IAM Roles

Roles used in this project:

**Screen Shot:**
"6- screen-shots/2- IAM-roles-and-policies-setup.jpg"

1. `usa-customs-glue-role`  
   → Execution role for all AWS Glue Jobs, Redshift and Crawlers.
   
2. `usa-customs-lambda-role`  
   → For future automation with AWS Lambda (e.g., triggering Glue Jobs).

3. `usa-customs-redshift-role`  
   → Allows Redshift to read data from S3 and access Glue Data Catalog (if needed).

4. `aws-quicksight-service-role`  
   → Allows Amazon QuickSight to connect to Redshift and (optionally) read sample data from S3.


---
## Permissions policies

## 1. `usa-customs-glue-role`

**Purpose:**  
Used by all Glue Jobs and Crawlers in this project.

**Permissions policies**

-AmazonAthenaFullAccess, AmazonRedshiftDataFullAccess, AmazonRedshiftFullAccess, 
AmazonS3FullAccess, AWSGlueServiceRole, CloudWatchLogsFullAccess

## 2. `usa-customs-lambda-role`

**Purpose:**  
Used by all connection between Redshift and reading sample data from S3.

**Permissions policies**

-AmazonS3FullAccess, AWSLambdaBasicExecutionRole

## 3. `usa-customs-redshift-role`

**Purpose:**  
Used by Redshift (Serverless workgroup) to read data from S3 and optionally use Glue Data Catalog.

**Permissions policies**

-AmazonRedshiftAllCommandsFullAccess, AmazonRedshiftFullAccess, AmazonS3ReadOnlyAccess

## 4. `aws-quicksight-service-role`

**Purpose:**  
Used by all Glue Jobs and Crawlers in this project.

**Permissions policies**

-AmazonAthenaFullAccess, AmazonAthenaFullAccess, AmazonRedshiftDataFullAccess, 
AmazonRedshiftFullAccess, AmazonS3FullAccess, AWSGlueServiceRole, CloudWatchLogsFullAccess

