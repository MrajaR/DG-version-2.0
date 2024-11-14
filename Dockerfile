# Use the official Python 3.11 image as the base image
FROM python:3.11.0-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies for building sqlite3, Tesseract, Poppler, and other required libraries
RUN apt-get update && \
    apt-get install -y wget build-essential libreadline-dev ffmpeg libsm6 libxext6 \
    poppler-utils tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

# Download, build, and install sqlite3 version 3.35.0 or later
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3430000.tar.gz && \
    tar xvfz sqlite-autoconf-3430000.tar.gz && \
    cd sqlite-autoconf-3430000 && \
    ./configure && make && make install && \
    cd .. && rm -rf sqlite-autoconf-3430000*

# Update the dynamic linker run-time bindings
RUN ldconfig

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install any required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Run the application
CMD ["python", "server.py"]
