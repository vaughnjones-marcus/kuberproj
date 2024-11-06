# Use Python base image
FROM python:3.9-slim
# Install Redis and Kubernetes client
RUN pip install redis kubernetes

# Copy the main Python file
COPY MFmon.py /app/MFmon.py

# Set the working directory
WORKDIR /app

# Set the entry point
CMD ["python", "MFmon.py"]
