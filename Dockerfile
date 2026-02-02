# Use Python slim image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script that reads MYSQL_URL
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash
set -e

# Use MYSQL_URL or DATABASE_URL
DB_URL="${MYSQL_URL:-$DATABASE_URL}"

if [ -z "$DB_URL" ]; then
  echo "ERROR: MYSQL_URL or DATABASE_URL must be set"
  exit 1
fi

# Extract connection details from mysql://user:password@host:port/database
DB_USER=$(echo "$DB_URL" | sed -E 's|mysql://([^:]+):.*|\1|')
DB_PASS=$(echo "$DB_URL" | sed -E 's|mysql://[^:]+:([^@]+)@.*|\1|')
DB_HOST=$(echo "$DB_URL" | sed -E 's|mysql://[^@]+@([^:]+):.*|\1|')
DB_PORT=$(echo "$DB_URL" | sed -E 's|mysql://[^@]+@[^:]+:([^/]+)/.*|\1|')
DB_NAME=$(echo "$DB_URL" | sed -E 's|mysql://[^/]+/([^?]+).*|\1|')

# Build SQLAlchemy URL
export DATABASE_URL="mysql+pymysql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

echo " Database configured: $DB_NAME on $DB_HOST:$DB_PORT"

# Start FastAPI with uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
EOF

RUN chmod +x /app/start.sh

EXPOSE 8000
CMD ["/app/start.sh"]
