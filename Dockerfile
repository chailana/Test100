# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Expose the port Flask will run on
EXPOSE 8000

# Run the start.sh script to start the processes
CMD ["./start.sh"]
