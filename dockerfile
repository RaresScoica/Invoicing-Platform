# # Use an official Python runtime as a parent image
# FROM python:3.10-slim

# # Set the working directory in the container
# WORKDIR /platform

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libssl-dev \
#     libffi-dev \
#     wkhtmltopdf \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Install wkhtmltopdf
# RUN apt-get update && apt-get install -y xvfb libfontconfig wkhtmltopdf

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Set environment variables
# ENV FLASK_APP=app.py

# # Make port 5000 available to the world outside this container
# EXPOSE 5000

# # Run the command to start the Flask app
# CMD ["flask", "run", "--host=0.0.0.0"]
