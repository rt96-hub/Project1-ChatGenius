FROM ubuntu:22.04

# Prevent timezone prompt during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and required system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    python3.11-venv \
    libmagic-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ensure we're using Python 3.11
RUN ln -s /usr/bin/python3.11 /usr/bin/python

COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/scripts/start.sh
ENTRYPOINT ["/app/scripts/start.sh"]