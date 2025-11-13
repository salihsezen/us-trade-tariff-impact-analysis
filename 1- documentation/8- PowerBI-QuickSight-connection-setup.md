> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 8- PowerBI-QuickSight-connection-setup.md  


This document explains how Power BI and Amazon QuickSight connect to the Redshift data warehouse.  
Formatted as one single markdown block without any nested code sections, suitable for direct GitHub use.

-------------------------------------------------------------------------------

#1. Overview

Both BI tools in this project use Redshift as the primary data source.  
The goal is to ensure a single source of truth for all KPI calculations, dashboards, and analytics.

The architecture is:

Redshift Core (Fact/Dim) → Power BI  
Redshift Core (Fact/Dim) → QuickSight

All BI semantics, measures, and DAX calculations use tables from the core schema.

-------------------------------------------------------------------------------

#2. Required Redshift Connection Information

**Screen Shot:**
"6- screen-shots/8.1- Redshift-work-group-info.jpg"

You will need the following:

• Hostname (Redshift workgroup endpoint)  
• Port: 5439  
• Database: dev  
• Username: dwh_admin or a dedicated read-only BI user  
• Password: stored securely in each BI tool  

Example endpoint format:

<workgroup-name>.<account-id>.us-east-1.redshift-serverless.amazonaws.com

This endpoint is found in:

AWS Console → Amazon Redshift → Serverless → Workgroup → General information

-------------------------------------------------------------------------------

#3. Power BI Connection Setup

**Screen Shot:**
"6- screen-shots/8.3- PowerBI-connection.jpg"

Steps inside Power BI Desktop:

1. Open Power BI Desktop.  
2. Select “Get Data”.  
3. Search and choose “Amazon Redshift”.  
4. Enter server (endpoint) and database name (dev).  
5. Choose Import or DirectQuery mode.  
   • Import = better performance for visuals.  
   • DirectQuery = real-time data from Redshift.  
6. Provide Redshift credentials.  
7. Navigate to schema and select tables:  
   • fact_trades  
   • dim_country  
   • dim_hts_category  
   • dim_direction  
   • dim_date  
8. Load the data into the Power BI model.  
9. Build relationships based on surrogate keys:  
   fact_trades.country_key → dim_country.country_key  
   fact_trades.hts6_key → dim_hts_category.hts6_key  
   fact_trades.direction_key → dim_direction.direction_key  
   fact_trades.date_key → dim_date.date_key  

After this, you can create DAX measures such as:  
Total Exports, Total Imports, Trade Balance, YoY Changes, Tariff Impact Score, etc.

-------------------------------------------------------------------------------

#4. Power BI Gateway Notes (If Needed)

If Power BI Service is used and the Redshift workgroup is NOT publicly accessible:

• Install Power BI On-Premises Gateway  
• Add Redshift as a data source inside the gateway  
• Provide the same credentials you used in Desktop  
• Publish the PBIX to Power BI Service  
• Map datasets to the gateway

If the workgroup is publicly accessible, the gateway may not be required.

-------------------------------------------------------------------------------

#5. QuickSight Connection Setup

**Screen Shot:**
"6- screen-shots/8.2- QuickSight-connection.jpg"

QuickSight must be in the same region as Redshift (us-east-1).

Steps:

1. Open Amazon QuickSight.  
2. Go to Datasets → New Dataset.  
3. Select Redshift as the data source.  
4. Enter connection details:  
   • Hostname  
   • Port 5439  
   • Database: dev  
   • Username & password  
5. Choose whether to import data into SPICE or use Direct Query.  
   • SPICE = faster dashboard loading  
   • Direct Query = real-time Redshift data  
6. Select tables from the core schema:  
   • core.fact_trades  
   • core.dim_country  
   • core.dim_hts_category  
   • core.dim_direction  
   • core.dim_date  
7. Join tables in QuickSight if needed or rely on the SQL model in Redshift.  
8. Build visuals normally.

-------------------------------------------------------------------------------

#6. IAM Role Requirements for QuickSight

QuickSight uses an IAM role to access Redshift:

aws-quicksight-service-role

Permissions required:

• AmazonRedshiftReadOnlyAccess or equivalent  
• Ability to connect to Redshift workgroup  
• (Optional) S3 read access if you use S3 files through Athena

Ensure that the QuickSight console → Security & permissions includes permission to access Redshift.

-------------------------------------------------------------------------------

#7. Connectivity Notes (Security, VPC, Accessibility)

• The Redshift workgroup must either be publicly accessible OR properly configured inside a VPC that QuickSight can reach.  
• If restricted by security groups, allow the IP range of QuickSight.  
• For Power BI, ensure your machine can connect to port 5439.  
• If needed, use SSL encryption (recommended for production).  
• Create BI-specific read-only users in Redshift to protect core tables.

-------------------------------------------------------------------------------

#8. Recommended Workflow for BI Tools

Preferred structure:

• All BI tools connect only to Redshift core schema  
• Do not connect directly to S3 or Glue Catalog  
• All heavy transformations should happen in Redshift or Glue  
• PBIX files reference stable table names, not staging tables  
• SPICE datasets refreshed daily or on demand  
• Power BI datasets refreshed with gateway or cloud connection  

This ensures stable, consistent KPIs across all dashboards.

-------------------------------------------------------------------------------

#9. Summary

To connect Power BI or QuickSight:

• Use Redshift endpoint, database, and user credentials  
• Always select tables from the core schema  
• Ensure the Redshift IAM role and network settings allow connectivity  
• Prefer Import/SPICE for performance  
• All ETL and modeling are completed before reaching BI  

Redshift is the master analytics source for the entire us-trade-tariff-analysis project.

-------------------------------------------------------------------------------
