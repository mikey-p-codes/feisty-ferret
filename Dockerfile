# Use an Ubuntu base image
FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages: Python, pip, sudo, and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    sudo \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-setuptools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user named 'valette'
# -m creates home directory /home/valette
# -s sets default shell
RUN useradd -m -s /bin/bash valette

# Add 'valette' to the sudo group [2]
RUN usermod -aG sudo valette

# Configure passwordless sudo for 'valette' [3, 2, 4, 5, 6]
# Create a file in /etc/sudoers.d for the user
RUN echo 'valette ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/valette-nopasswd && \
    chmod 0440 /etc/sudoers.d/valette-nopasswd

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt.

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the Flask application code into the container
COPY app.py.

# Create the insecure upload directory and set permissions
# Note: This path matches UPLOAD_FOLDER in app.py
RUN mkdir -p /app/uploads && \
    chmod -R 777 /app/uploads && \
    chown -R valette:valette /app/uploads

# Expose the port Gunicorn will run on
EXPOSE 8000

# Switch to the non-root user 'valette'
# Gunicorn will run as this user, but 'valette' can use passwordless sudo
USER valette

# Command to run the application using Gunicorn
# Binds to 0.0.0.0:8000 to be accessible outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]