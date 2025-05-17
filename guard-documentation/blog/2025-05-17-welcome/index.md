---
slug: minimal-mvp-guard
title: Minimal MVP of Guard
authors: [alan-insam]
---

# Minimal MVP of Guard

For the minimal viable product (MVP) of the Guard project, the focus is on providing a streamlined, on-premises solution for detecting and redacting sensitive information from PDF documents, without the complexity of frontend or traditional backend web applications.

<!-- truncate -->

## Core Components

- **CLI Tool:**  
  A Python command-line utility that processes PDF files, extracts their text, and interacts with the Guard API for PII detection. It can redact or highlight sensitive information directly within documents.

- **API Server:**  
  A lightweight REST API (Flask-based) that exposes endpoints for text analysis, entity recognition, and health checks. It leverages Microsoft Presidio and custom NLP models for robust PII detection.

- **Recognizer Registry:**  
  Built-in and custom recognizers (such as for emails, phone numbers, and Austrian license plates) extend detection capabilities.

- **Configuration:**  
  Flexible YAML configuration allows fine-tuning of models, thresholds, and supported languages (German, English, Italian).

- **Deployment:**  
  Designed to run entirely on-premises, with optional containerization (e.g., via K3s) for scalable and secure deployment.

## What’s Not Included (MVP Scope)

- No web-based frontend or traditional backend application.
- No user authentication or multi-user management.
- No cloud dependencies—Guard runs fully local for maximum data privacy.

## Getting Started

- Use the CLI tool to process your PDF files.
- The API server must be running locally or on your secure network.
- Configure recognizers and models as needed in the YAML config.

---

This minimal MVP approach ensures Guard is simple to deploy, privacy-focused, and easy to extend as new requirements arise.