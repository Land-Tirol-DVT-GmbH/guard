# Dockerfile
FROM mcr.microsoft.com/presidio-analyzer:latest

# Set working directory
WORKDIR /app

# Copy your Flask app and support files
COPY app.py /app/app.py
COPY utils/ /app/utils/
COPY config /app/config/
COPY core /app/core/

# Install spaCy models and transformers
RUN pip install flask python-dotenv presidio_analyzer[transformers] flair[embeddings]

# Use your custom app.py as the entrypoint
ENV FLASK_APP=app.py
ENV ANALYZER_CONF_FILE=/app/config/full_analyzer_config.yaml
CMD ["python3", "app.py"]
