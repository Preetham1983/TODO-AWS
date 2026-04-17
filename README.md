# 📋 TODO Microservice Application

A full-stack TODO application built with **clean architecture**, **SOLID principles**, and a **microservice** topology. Each service is independently dockerized, uses **UV** for Python packaging, and connects to **LocalStack** for AWS S3 & SES emulation.

---

## 🏗️ Architecture Overview

```
┌──────────┐
│  Nginx   │ ← Reverse proxy (port 80)
│ (port 80)│
└────┬─────┘
     │  Routes /api/v1/todos/*         → todo-service:8001
     │  Routes /api/v1/attachments/*   → attachment-service:8002
     │  Routes /api/v1/notifications/* → notification-service:8003
     │  Routes /*                      → frontend:3000
     │
     ├── Todo Service          (FastAPI, port 8001)
     ├── Attachment Service    (FastAPI, port 8002, S3 via LocalStack)
     ├── Notification Service  (FastAPI, port 8003, SES via LocalStack)
     ├── Frontend              (React, port 3000)
     └── LocalStack            (AWS emulator, port 4566)
```

## 📂 Project Structure

```
TODO/
├── docker-compose.yml          # Orchestrates all services
├── .env.docker                 # Shared environment variables
├── .gitignore
├── scripts/
│   └── init_localstack.sh      # S3 bucket + SES identity setup
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf              # Reverse proxy configuration
├── services/
│   ├── todo_service/           # Manages TODO items
│   │   ├── Dockerfile
│   │   ├── pyproject.toml      # UV / ruff / pylint config
│   │   └── src/todo_service/
│   │       ├── config/         # Pydantic Settings
│   │       ├── domain/         # Entities + Repository interfaces
│   │       ├── application/    # Use cases + DTOs
│   │       ├── infrastructure/ # In-memory repository adapter
│   │       └── presentation/   # FastAPI controllers
│   ├── attachment_service/     # File uploads via S3
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── src/attachment_service/
│   │       ├── config/
│   │       ├── domain/
│   │       ├── application/
│   │       ├── infrastructure/ # S3 storage adapter (boto3)
│   │       └── presentation/
│   └── notification_service/   # Email via SES
│       ├── Dockerfile
│       ├── pyproject.toml
│       └── src/notification_service/
│           ├── config/
│           ├── domain/
│           ├── application/
│           ├── infrastructure/ # SES email adapter (boto3)
│           └── presentation/
└── frontend/                   # React dark-theme UI
    ├── Dockerfile
    ├── package.json
    ├── public/
    └── src/
        ├── services/           # ApiClient + service classes
        └── components/         # Header, TodoForm, TodoList, etc.
```

## 🚀 Quick Start

```bash
# 1. Clone the repo
cd TODO

# 2. Start everything
docker compose up --build

# 3. Open the app
#    Frontend:       http://localhost
#    Todo API docs:  http://localhost:8001/api/v1/todos/docs
#    Attach API docs: http://localhost:8002/api/v1/attachments/docs
#    Notif API docs: http://localhost:8003/api/v1/notifications/docs
#    LocalStack:     http://localhost:4566
```

## 🔌 LocalStack Integration

### How it works

| AWS Service | LocalStack Endpoint | Purpose |
|---|---|---|
| **S3** | `http://localhost:4566` | File storage for TODO attachments |
| **SES** | `http://localhost:4566` | Email notifications |

### Connection Details

- **Endpoint URL**: `http://localstack:4566` (Docker internal) / `http://localhost:4566` (host)
- **Credentials**: `aws_access_key_id=test`, `aws_secret_access_key=test`
- **Region**: `us-east-1`
- **S3 addressing**: `path` style (virtual-hosted won't resolve on LocalStack)

### Verifying LocalStack

```bash
# Check health
curl http://localhost:4566/_localstack/health

# List S3 buckets
aws --endpoint-url=http://localhost:4566 s3 ls

# List SES identities
aws --endpoint-url=http://localhost:4566 ses list-identities --region us-east-1

# View sent emails (LocalStack dashboard)
curl http://localhost:4566/_aws/ses
```

## 🧱 Clean Architecture Layers

Each Python service follows a 4-layer clean architecture:

| Layer | Responsibility | Depends on |
|---|---|---|
| **Domain** | Entities, enums, repository interfaces | Nothing |
| **Application** | Use cases, DTOs | Domain |
| **Infrastructure** | Concrete adapters (S3, SES, in-memory) | Domain |
| **Presentation** | FastAPI controllers (HTTP) | Application |

### SOLID Principles Applied

- **S** – Single Responsibility: Controllers only translate HTTP; use cases only orchestrate; adapters only talk to infra
- **O** – Open/Closed: Add a new storage backend by implementing `StorageServiceInterface`
- **L** – Liskov Substitution: All adapters are interchangeable via their interface
- **I** – Interface Segregation: Small, focused interfaces per concern
- **D** – Dependency Inversion: Domain defines interfaces; infrastructure implements them

## 🛠️ Development

### Per-service dev setup (example: todo_service)

```bash
cd services/todo_service

# Install uv (if not installed)
pip install uv

# Install deps
uv sync

# Run dev server
uv run uvicorn src.todo_service.main:create_application --factory --reload --port 8001

# Lint
uv run ruff check src/
uv run pylint src/
```

## 📡 API Endpoints

### Todo Service (`/api/v1/todos`)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/todos` | Create a TODO |
| GET | `/api/v1/todos` | List all TODOs |
| GET | `/api/v1/todos/search?q=` | Search TODOs |
| GET | `/api/v1/todos/{id}` | Get single TODO |
| PUT | `/api/v1/todos/{id}` | Update a TODO |
| DELETE | `/api/v1/todos/{id}` | Delete a TODO |

### Attachment Service (`/api/v1/attachments`)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/attachments/upload/{todo_id}` | Upload a file |
| GET | `/api/v1/attachments/todo/{todo_id}` | List attachments for TODO |
| GET | `/api/v1/attachments/{id}` | Get attachment metadata |
| GET | `/api/v1/attachments/{id}/download` | Download file |
| DELETE | `/api/v1/attachments/{id}` | Delete attachment |

### Notification Service (`/api/v1/notifications`)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/notifications/send` | Send email notification |
| GET | `/api/v1/notifications` | List all notifications |
| GET | `/api/v1/notifications/{id}` | Get single notification |
| GET | `/api/v1/notifications/identities` | List SES verified emails |

## 🐳 Docker Commands

```bash
# Build and start all services
docker compose up --build

# Start in detached mode
docker compose up -d --build

# View logs
docker compose logs -f todo-service
docker compose logs -f attachment-service
docker compose logs -f notification-service

# Stop everything
docker compose down

# Stop and remove volumes
docker compose down -v
```
"# TODO-AWS" 
