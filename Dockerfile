# Use an x86_64 based parent image
FROM --platform=linux/amd64 python:3.10-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y wget curl unzip jq xvfb xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic

# Install additional Qt libraries
RUN apt-get install -y libxrender1 libfontconfig1 libqt5gui5 libqt5webkit5 libqt5network5 libqt5core5a

# Install wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb && \
    dpkg -i wkhtmltox_0.12.6.1-2.bullseye_amd64.deb && \
    rm wkhtmltox_0.12.6.1-2.bullseye_amd64.deb

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