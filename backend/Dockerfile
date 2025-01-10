FROM python:3.11

WORKDIR /app

COPY requirements2.txt .
RUN pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements2.txt

COPY . .
RUN chmod +x /app/scripts/start.sh
ENTRYPOINT ["/app/scripts/start.sh"]