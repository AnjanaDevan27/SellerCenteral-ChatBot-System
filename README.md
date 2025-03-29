# SellerCenteral-ChatBot-System

## Overview
This project implements a chatbot for the Seller Central platform that helps users manage seller data efficiently. The pipeline processes JSONL data files, assigns seller IDs to products, and generates a merged CSV file. This repository also integrates with Google Cloud Storage (GCS) to handle the data.

---

## Table of Contents

- [Environment Setup](#environment-setup)
- [Pipeline Execution](#pipeline-execution)
- [Code Structure](#code-structure)
- [Reproducibility & Data Versioning](#reproducibility--data-versioning)
- [Code Style & Guidelines](#code-style--guidelines)
- [Error Handling & Logging](#error-handling--logging)
- [Contributing](#contributing)

---

## Environment Setup

Follow these steps to set up the environment on your local machine:

1. *Clone the repository:*
   bash
   git clone https://github.com/your-repo-name/seller-central-chatbot.git
   cd seller-central-chatbot
2. **Create and activate a virtual environment:**

- For Python 3.x:
    bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    
3. *Install the required dependencies:*
    bash
    pip install -r requirements.txt


4. **Set up Google Cloud credentials:**
- Ensure you have a Google Cloud project and the necessary permissions to access GCS.
- Download your credentials.json from the Google Cloud Console and set the environment variable:
  
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
  

5. **DVC Setup (for data versioning):**
- Install DVC if not already installed:
  
  pip install dvc
  
- Initialize DVC in the repository:
  
  dvc init
  
- Pull the data files if they are tracked in DVC:
  
  dvc pull
  

## Pipeline Execution

To run the pipeline and process the data, follow these steps:

### **1. Ensure all dependencies are installed**  
If dependencies are missing, install them using:
bash
pip install -r requirements.txt


### **2. Activate the virtual environment**  
bash
source venv/bin/activate  # On Windows: venv\Scripts\activate


### **3. Run the pipeline script**  

#### **Run the Data Pipeline manually:**  
bash
python Data_pipeline/dags/fetch_data.py        # Fetch raw data
python Data_pipeline/dags/data_process.py      # Process raw data
python Data_pipeline/dags/bias_detection.py    # Detect bias in data
python Data_pipeline/dags/dataflow_processing.py # Perform dataflow processing
python Data_pipeline/dags/sellerId_check.py    # Validate seller ID information
python Data_pipeline/dags/mlops_airflow.py     # Run MLOps integration


#### **Run the pipeline using Apache Airflow:**  
bash
airflow db init                      # Initialize Airflow database
airflow scheduler &                   # Start Airflow scheduler
airflow webserver --port 8080         # Start Airflow webserver (http://localhost:8080)

**Enable and trigger DAGs inside Airflow UI:**.

### **4. Monitor the output**  
- The processed output files will be stored in the **data/** folder.  
- Bias detection logs will be stored in **Data_pipeline/dags/bias_detection.log**.  
- Execution logs will be printed to the terminal and stored in **logs/pipeline.log**.  
- If using **Google Cloud Storage (GCS)**, processed files will be stored in **processed/** on GCS.  

## Code Structure

Here's a breakdown of the project's folder and file structure:

```
 SellerCentral-Chatbot-System/
 │
 ├── Data_pipeline/              # Main data pipeline directory
 │   ├── .dvc/                   # Data Version Control (DVC) metadata
 │   │   ├── .gitignore
 │   │   ├── config
 │   │
 │   ├── dags/                    # Apache Airflow DAGs (Directed Acyclic Graphs)
 │   │   ├── __pycache__/         # Cached compiled Python files
 │   │   ├── bias_detection.py    # Bias detection logic
 │   │   ├── config.py            # Configuration settings
 │   │   ├── data_process.py      # Data processing logic
 │   │   ├── dataflow_processing.py  # Main dataflow script
 │   │   ├── fetch_data.py        # Fetches raw data from GCS
 │   │   ├── logging_setup.py     # Logging configurations
 │   │   ├── mlops_airflow.py     # MLOps integration with Airflow
 │   │   ├── sellerId_check.py    # Data validation script
 │   │   ├── .gitignore           # Ignore unnecessary files
 │   │   ├── bias_detection.log   # Bias detection logs
 │   │
 │   ├── data/                    # Data directory (tracked via DVC)
 │   │   ├── .gitignore
 │   │   ├── new_data_sentiment.csv.dvc  # Tracked dataset
 │   │
 │   ├── logs/                    # Logs for debugging and monitoring
 │   │   ├── .gitignore
 │   │   ├── pipeline.log         # Execution logs
 │   │
 │   ├── tests/                   # Tests for pipeline validation
 │   │   ├── __init__.py          # Makes tests a package
 │   │   ├── test_fetch_data.py     # Test for fetch_data.py (GCS Extraction)
 │   │   ├── test_data_process.py   # Test for data_process.py (Transformation)
 │   │   ├── test_bias_detection.py # Test for bias_detection.py
 │   │   ├── test_pipeline.py       # Integration test for full ETL pipeline
 │   │   ├── test_schema.py         # Test for data schema validation (BigQuery)
 │   │   ├── test_dvc.py            # Test for DVC data versioning
 │   │   ├── test_airflow.py        # Test for Airflow DAG execution
 │
 ├── .github/workflows/             # CI/CD automation for testing
 │   ├── ci.yml                     # GitHub Actions workflow for local testing
 │   ├── ci-gcp.yml                  # GitHub Actions workflow for GCP testing
 │
 ├── docker-compose.yml           # Docker Compose file for container orchestration
 ├── Dockerfile                   # Docker setup for the project
 ├── requirements.txt              # Python dependencies
 ├── .gitignore                    # Ignore unnecessary files
 └── README.md                     # Documentation
```

## Reproducibility & Data Versioning

- ensure reproducibility, follow these steps:

1. Clone the repository and install dependencies: As described in the Environment Setup section.

2. Use DVC to version the data: The data files are versioned with DVC. Use DVC to pull the latest data when setting up the project:

    bash
    dvc pull

3. Re-run the pipeline: Once the environment is set up and dependencies installed, you can re-run the pipeline with:

    ```bash
    python scripts/sellerId_check.py


This will ensure that the data, code, and environment are consistent across different machines.

## Code Style & Guidelines

The code in this repository follows Python's PEP 8 guidelines for readability and consistency.

- *Modular Programming:* The code is divided into smaller, reusable functions for clarity and maintainability.
- *Naming Conventions:* Variables, functions, and classes use descriptive and consistent naming conventions as per PEP 8.
- *Documentation:* All functions and classes are documented with docstrings to explain their purpose and usage.

## Error Handling & Logging

The project includes error handling to ensure smooth execution and provide detailed logs for troubleshooting.

- *File Processing Errors:* If the JSONL data files are malformed or missing, the script will print warnings and skip those files.
- *Data Unavailability:* The pipeline checks if required columns like parent_asin are missing, and logs appropriate error messages.
- *Logging:* The project uses print statements to log progress, errors, and warnings. You can customize this to use a more advanced logging framework like logging for better control.

## Contributing

Contributions are welcome! If you want to improve the project, follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Commit your changes.
4. Push your branch and create a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Example Code Snippets

**Example: How to use the assign_seller_id function**
