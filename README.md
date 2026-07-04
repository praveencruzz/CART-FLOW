<<<<<<< HEAD
# 🛒 CartFlow – End-to-End Data Engineering Pipeline

An end-to-end Data Engineering project that transforms raw e-commerce data into analytics-ready datasets using a modern data stack. The project demonstrates data ingestion, transformation, dimensional modeling, and interactive business reporting using Snowflake, dbt, SQL, and Power BI.

---

# 📌 Project Overview

This project implements a complete ELT pipeline for an e-commerce dataset. Raw CSV files are loaded into Snowflake, transformed using dbt, modeled into a star schema, and visualized through an interactive Power BI dashboard.

The objective of the project is to demonstrate modern Data Engineering practices including data warehousing, modular transformations, dimensional modeling, data quality testing, and business analytics.

---

# 🏗️ Architecture

```
                 Raw E-commerce CSV Files
                           │
                           ▼
                Python Data Ingestion
                           │
                           ▼
               PySpark Data Processing
                           │
                           ▼
            Snowflake Bronze Layer (Raw)
                           │
                           ▼
             dbt Staging Models (Cleaned)
                           │
                           ▼
         dbt Intermediate Models (Business Logic)
                           │
                           ▼
     dbt Mart Models (Fact & Dimension Tables)
                           │
                           ▼
                  SQL Business Analytics
                           │
                           ▼
                 Power BI Interactive Dashboard

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Data Processing |
| SQL | Data Transformation |
| Snowflake | Cloud Data Warehouse |
| dbt | ELT & Data Transformation |
| Power BI | Dashboard & Reporting |
| Git & GitHub | Version Control |

---

# 📂 Project Structure

```
## 📂 Project Structure

```text
CartFlow/
│
├── cartflow_dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── tests/
│   ├── macros/
│   ├── target/
│   ├── dbt_project.yml
│   └── packages.yml
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
│
├── python/
│   ├── ingest.py
│   └── generate_supplemental_data.py
│
├── pyspark/
│   └── process.py
│
├── snowflake/
│   ├── 01_database.sql
│   ├── 02_file_formats.sql
│   ├── 03_stages.sql
│   ├── 04_bronze_tables.sql
│   ├── 05_copy_into.sql
│   ├── 06_gold_tables.sql
│   └── 08_analytics.sql
│
├── powerbi/
│   ├── dashboard_img1.png
│   ├── dashboard_img2.png
│   ├── dashboard_img3.png
│   └── powerbi_model.png
│
├── docs/
│   ├── architecture.md
│   ├── dbt_lineage.png
│   └── dbt_docs.png
│
├── logs/
│
├── requirements.txt
├── .gitignore
├── .gitattributes
└── README.md
```
```

---

# ⚙️ Data Pipeline

### Step 1 – Data Ingestion

Loaded raw e-commerce CSV files into Snowflake Bronze tables.

### Step 2 – Data Transformation

Created dbt source definitions and staging models to clean and standardize the raw data.

### Step 3 – Intermediate Models

Combined staging models and applied business transformations to prepare analytical datasets.

### Step 4 – Data Modeling

Designed a Star Schema consisting of:

### Fact Tables

- fact_orders
- fact_payments

### Dimension Tables

- dim_customer
- dim_product
- dim_seller
- dim_date

### Step 5 – Documentation & Testing

Implemented dbt documentation, lineage graph, and data quality tests using:

- unique
- not_null
- relationships

### Step 6 – Business Intelligence

Connected dbt mart models to Power BI and created an interactive dashboard.

---

# 📊 Dashboard Features

The dashboard includes the following KPIs and visualizations:

- Total Revenue
- Total Orders
- Total Customers
- Average Order Value (AOV)
- Average Review Score
- Monthly Revenue Trend
- Top 10 Products
- Top Sellers
- Payment Method Analysis

---

# 📷 Project Screenshots

## Power BI Dashboard

->DASHBOARD_IMG1.JPEG
->DASHBOARD_IMG2.JPEG
->DASHBOARD_IMG3.JPEG
## Power BI Data Model

->MODEL_POWERBI.JPEG

## dbt Lineage Graph

->DBT_LINEAGE.PNG

## dbt Documentation

->DBT_DOC.PNG

---

# 🧪 Data Quality

Implemented data validation using dbt tests:

- Unique Tests
- Not Null Tests
- Relationship Tests

---

# 📈 Business Analytics

The project supports business analysis including:

- Monthly Revenue
- Customer Lifetime Value (CLV)
- Average Order Value (AOV)
- Top Selling Products
- Top Sellers
- Monthly Sales Trends
- Payment Method Analysis
- Customer Insights

---

# 🚀 Getting Started

### Clone Repository

```bash
git clone https://github.com/yourusername/CartFlow.git
```

### Configure dbt

Update your Snowflake credentials in:

```
profiles.yml
```

### Run Models

```bash
dbt run
```

### Run Tests

```bash
dbt test
```

### Generate Documentation

```bash
dbt docs generate
dbt docs serve
```

---

# 💡 Skills Demonstrated

- Data Engineering
- Data Warehousing
- ETL / ELT Pipelines
- Snowflake
- dbt
- SQL
- Data Modeling
- Star Schema Design
- Power BI
- Data Quality Testing
- Git & GitHub

---

# 🔮 Future Enhancements

- Integrate AWS S3 for cloud-based data ingestion.
- Automate data loading using Snowpipe.
- Schedule workflows using Snowflake Tasks.
- Add orchestration using Apache Airflow.
- Integrate PySpark for large-scale data processing.

---

# 👨‍💻 Author

**Praveen Raj**

Computer Science Engineer | Data Engineering Enthusiast

GitHub: https://github.com/praveencruzz

LinkedIn: https://linkedin.com/in/praveensaravanakumar
=======
# CART-FLOW
End-to-end data engineering project using Snowflake, dbt, Python, and SQL to build scalable ELT pipelines for e-commerce analytics.
>>>>>>> fce7ee79a8fec5309f2a686fe2479d621e0e331b
