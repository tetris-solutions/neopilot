FROM python:3.11-slim

WORKDIR /app

# Install package dependencies first (layer cache)
COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir .

# Data directory for instance storage
RUN mkdir -p /data
ENV NEOPILOT_DATA_DIR=/data

# HTTP transport defaults
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

EXPOSE 8000

CMD ["python", "-m", "neopilot.server"]
