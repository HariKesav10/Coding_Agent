FROM python:3.11-slim
LABEL authors="HariKesav"

# 1. Install system dependencies if needed, then pre-install python libraries
RUN pip install --no-cache-dir numpy pandas pytest requests matplotlib scipy

# 2. Setup isolated user
RUN useradd -m -s /bin/bash sandboxuser

# 3. Setup workspace directory
WORKDIR /workspace
RUN chown -R sandboxuser:sandboxuser /workspace

USER sandboxuser

# Default command if none is passed
CMD ["python3"]