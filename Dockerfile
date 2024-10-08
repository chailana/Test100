# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*  # Clean up

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot code into the container
COPY . .

# Expose the port for the app
EXPOSE 8080

# Command to run your bot using gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]
