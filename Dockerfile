# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY server/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server source code into the container
COPY ./server /app/server

# Copy the machine learning model into the container
# This ensures the relative path ../mlmodel in ml_detector.py works correctly
COPY ./mlmodel /app/mlmodel

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the app. Use 0.0.0.0 to make it accessible from the host.
# The entry point is the 'app' object in 'server/main.py'
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]