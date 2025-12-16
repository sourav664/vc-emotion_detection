# =========================
# Stage 1: Builder
# =========================
FROM python:3.10-slim-bookworm AS builder

# Set work directory
WORKDIR /app

# Install system dependencies only if needed for compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage caching
COPY ./flask_app/requirements.txt .

# Install dependencies using pre-built binaries where possible
RUN pip install --prefix=/install --no-cache-dir --prefer-binary -r requirements.txt

# Download NLTK data inside builder (isolated)
RUN mkdir -p /nltk_data && \
    PYTHONPATH=/install/lib/python3.10/site-packages \
    python -m nltk.downloader -d /nltk_data stopwords wordnet

# Remove build tools to shrink builder layer
RUN apt-get purge -y build-essential gcc && apt-get autoremove -y


# =========================
# Stage 2: Final Image
# =========================
FROM python:3.10-slim-bookworm AS final

# Set working directory
WORKDIR /app

# Copy installed Python packages and NLTK data from builder
COPY --from=builder /install /usr/local
ENV NLTK_DATA=/usr/local/nltk_data
COPY --from=builder /nltk_data ${NLTK_DATA}

# Copy only necessary application files (reduces size)
COPY ./flask_app/app.py .
COPY ./flask_app/templates/ ./templates/
COPY ./models/ ./models/

# Add environment variable and expose port
ENV PORT=5000
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]