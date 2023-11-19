# Use the official Python image as the base image
FROM python:3.10.6-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
COPY retrieve_images.py .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "retrieve_images.py"]

