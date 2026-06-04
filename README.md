# 🚀 Aura Notes API

A FastAPI backend with MongoDB, Google Cloud Storage, and Gemini AI integration.

## 🏗️ Architecture Diagram

```mermaid
graph TD
    %% Define styles
    classDef client fill:#f9f,stroke:#333,stroke-width:2px;
    classDef router fill:#bbf,stroke:#333,stroke-width:2px;
    classDef service fill:#bfb,stroke:#333,stroke-width:2px;
    classDef db fill:#ffb,stroke:#333,stroke-width:2px;
    classDef ext fill:#fbb,stroke:#333,stroke-width:2px;

    %% Client Layer
    Client["📱 Client App (Web / Mobile)"]:::client

    %% Core Application entry
    FastAPI["🚀 FastAPI Entry (src/main.py)"]:::router

    %% Modules / Domains
    subgraph auth ["🔐 Auth Module"]
        auth_router["router.py"]:::router
        auth_service["service.py"]:::service
        auth_models["models.py (User, OTP)"]:::db
    end

    subgraph intake ["📥 Intake Module"]
        intake_router["router.py"]:::router
        intake_service["service.py"]:::service
        intake_models["models.py (UploadedImage)"]:::db
    end

    subgraph preprocess ["⚙️ Preprocess Module"]
        prep_service["service.py (normalize, contrast)"]:::service
        prep_adapter["adapter.py"]:::service
        prep_utils["utils.py (cv2)"]:::service
    end

    subgraph ocr ["🔍 OCR Module"]
        ocr_router["router.py"]:::router
        ocr_service["service.py"]:::service
        ocr_clients["OCR Clients (Paddle, Gemini)"]:::ext
        ocr_models["models.py (BusinessCardScan)"]:::db
    end

    subgraph pipeline ["🔗 Pipeline Module"]
        ocr_pipeline["ocr_pipeline.py (Orchestrator)"]:::service
    end

    subgraph mapping ["🗺️ Field Mapping Module"]
        mapping_service["service.py (mapper)"]:::service
    end

    subgraph confidence ["📊 Confidence Module"]
        conf_router["router.py"]:::router
        conf_service["service.py"]:::service
    end

    subgraph review ["📝 Review Module"]
        review_router["router.py"]:::router
        review_service["service.py"]:::service
    end

    %% External & Shared Services
    MongoDB[("🗄️ Shared MongoDB (via Beanie)")]:::db
    GCS[("☁️ Google Cloud Storage (Blobs)")]:::ext

    %% Flow of requests
    Client -->|HTTP requests| FastAPI
    FastAPI --> auth_router
    FastAPI --> intake_router
    FastAPI --> ocr_router
    FastAPI --> conf_router
    FastAPI --> review_router

    %% Auth Layer interactions
    auth_router --> auth_service
    auth_service --> auth_models
    auth_models --> MongoDB

    %% Document Upload & Processing Orchestration Flow
    intake_router --> intake_service
    intake_service --> intake_models
    intake_models --> MongoDB
    intake_service -->|Upload raw files| GCS

    %% OCR Pipeline execution (Orchestrator)
    ocr_router --> ocr_pipeline
    ocr_pipeline -->|1. Fetch image records| MongoDB
    ocr_pipeline -->|2. Download blobs| GCS
    ocr_pipeline -->|3. Clean images| prep_adapter
    prep_adapter --> prep_service
    prep_service --> prep_utils
    ocr_pipeline -->|4. Detect text & map| ocr_service
    ocr_service --> ocr_clients
    ocr_service --> ocr_models
    ocr_models --> MongoDB
```

## 📁 Project Structure



```text
fastapi-project
├── alembic/            # Database migrations management (SQL only, Mongo does not need)
├── src/
│   ├── auth/           # Authentication Domain
│   │   ├── router.py, schemas.py, models.py, dependencies.py, config.py, 
│   │   └── constants.py, exceptions.py, service.py, utils.py
│   ├── gcp/            # Google Cloud Platform Domain
│   ├── posts/          # Posts Domain
│   │   ├── router.py, schemas.py, models.py, dependencies.py, constants.py,
│   │   └── exceptions.py, service.py, utils.py
│   ├── main.py         # Application entry point & initialization
│   ├── config.py       # Global configuration settings
│   ├── database.py     # Database connection & session management
│   ├── models.py       # Global/Shared base models
│   ├── exceptions.py   # Global exception handlers
│   └── pagination.py   # Global pagination utility module
├── tests/              # Test suite (organized by domain)
│   ├── auth/
│   ├── gcp/            # Formerly AWS, now using GCP
│   └── posts/
├── templates/          # Frontend templates (not use)
│   └── index.html
```
├── requirements/       # Dependency management
│   ├── base.txt, dev.txt, prod.txt
├── .env                # Environment variables
├── .gitignore          # Git ignore file
├── logging.ini         # Logging configuration
└── alembic.ini         # Alembic migration configuration
```
Getting Started
### 1. Install Dependencies
Choose the appropriate requirements file for your environment:

```bash
pip install -r requirements/dev.txt
```
### 2. Run the Application
Start the development server using Uvicorn:

```bash
uvicorn src.main:app --reload
```
### 3. API Documentation
Once the server is running, you can access the interactive Swagger UI at:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
