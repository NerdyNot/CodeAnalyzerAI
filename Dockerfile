# Use an x86_64 based parent image
FROM --platform=linux/amd64 python:3.10-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y wget curl unzip jq wkhtmltopdf

# Install SQLCheck
RUN wget https://github.com/jarulraj/sqlcheck/releases/download/v1.3/sqlcheck-x86_64.deb && \
    dpkg -i sqlcheck-x86_64.deb && \
    rm sqlcheck-x86_64.deb

# Install Horusec
RUN curl -fsSL https://github.com/ZupIT/horusec/releases/download/v2.8.0/horusec_linux_amd64.deb -o horusec.deb && \
    dpkg -i horusec.deb && \
    mv /usr/local/bin/horusec_linux_amd64 /usr/local/bin/horusec && \
    rm horusec.deb

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
