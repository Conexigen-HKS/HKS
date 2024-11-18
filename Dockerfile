# Use an official Python runtime as a parent image
FROM python:3.12.3-slim

# Upgrade pip
RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the FastAPI app code
COPY ./app /app

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
