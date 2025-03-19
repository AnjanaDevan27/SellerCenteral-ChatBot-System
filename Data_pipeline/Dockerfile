# Use an official Python runtime as a parent image
FROM apache/airflow:2.6.0 AS builder

# Set the working directory in the container
WORKDIR /opt/airflow

# Copy the current directory contents into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip 
RUN pip install --user --no-cache-dir -r requirements.txt

# Start a new stage for a smaller final image
FROM apache/airflow:2.6.0

# Copy installed packages from builder stage
COPY --from=builder /home/airflow/.local /home/airflow/.local

# Make sure scripts in .local are usable:
ENV PATH=/home/airflow/.local/bin:$PATH

# Set the working directory to /opt/airflow
WORKDIR /opt/airflow

# Copy your DAGs
COPY ./dags /opt/airflow/dags
COPY ./plugins /opt/airflow/plugins

# Expose the port the app runs on
EXPOSE 8080

# Run airflow webserver when the container launches
CMD ["airflow", "webserver"]
