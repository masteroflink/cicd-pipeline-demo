# CI/CD Pipeline Demo

A production-ready CI/CD pipeline demonstration using GitHub Actions and Docker. This project showcases automated testing, building, and deployment of a containerized Python FastAPI application.

## Features

- **FastAPI REST API** with health checks, CRUD operations, and calculator endpoints
- **Test-Driven Development (TDD)** with 100% code coverage
- **Multi-stage Docker builds** for optimized production images
- **GitHub Actions CI/CD** with lint, test, build, and deploy stages
- **Container Registry** integration with GitHub Container Registry (ghcr.io)
- **Security scanning** with Trivy vulnerability scanner
- **Automated releases** with semantic versioning

## Pipeline Overview

```
+-------------+     +-------------+     +-------------+     +-------------+
|    Lint     | --> |    Test     | --> |    Build    | --> |   Deploy    |
| black/ruff  |     | pytest/cov  |     | Docker push |     |   staging   |
+-------------+     +-------------+     +-------------+     +-------------+
                          |
                          v
                    +-----------+
                    | Coverage  |
                    |  Report   |
                    +-----------+
```

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/masteroflink/cicd-pipeline-demo.git
cd cicd-pipeline-demo

# Build and run
docker compose up --build

# Access the API
curl http://localhost:8000/health
```

### Using Make

```bash
# Build the development image
make build

# Start the server
make up

# Run tests
make test

# Run tests with coverage
make test-cov

# Run linting
make lint
```

### Using the Published Image

```bash
# Pull the latest image
docker pull ghcr.io/masteroflink/cicd-pipeline-demo:latest

# Run the container
docker run -p 8000:8000 ghcr.io/masteroflink/cicd-pipeline-demo:latest

# Access the API
curl http://localhost:8000/health
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with status, version, timestamp |
| GET | `/api/v1/items` | List all items |
| POST | `/api/v1/items` | Create a new item |
| GET | `/api/v1/items/{id}` | Get item by ID |
| POST | `/api/v1/calculate` | Perform calculation (add, subtract, multiply, divide) |

### Example Requests

```bash
# Health check
curl http://localhost:8000/health

# Create an item
curl -X POST http://localhost:8000/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Example", "description": "An example item"}'

# Calculate
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5, "operation": "add"}'
```

## Development

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development without Docker)
- Make (optional, for convenience commands)

### Project Structure

```
cicd-pipeline-demo/
├── .github/workflows/     # GitHub Actions workflows
│   ├── ci.yml            # CI pipeline (lint, test, build)
│   ├── cd.yml            # CD pipeline (deploy to staging)
│   └── release.yml       # Release workflow (tag-triggered)
├── src/app/              # Application source code
│   ├── api/              # API endpoints
│   ├── models/           # Pydantic models
│   └── services/         # Business logic
├── tests/                # Test suite
├── docker/               # Dockerfiles
├── scripts/              # Deployment scripts
└── Makefile              # Development commands
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
docker compose run --rm api pytest tests/test_calculator.py -v
```

### Linting

```bash
# Check all linting
make lint

# Auto-format code
make format
```

## CI/CD Workflows

### CI Pipeline (`.github/workflows/ci.yml`)

Triggered on push/PR to `main` and `develop` branches:

- **Lint**: Black, Ruff, Mypy
- **Test**: pytest with coverage report
- **Build**: Docker image build and push (main only)
- **Security**: Trivy vulnerability scan (main only)

### CD Pipeline (`.github/workflows/cd.yml`)

Triggered on push to `main`:

- Pulls latest image from ghcr.io
- Simulates staging deployment
- Runs smoke tests

### Release Pipeline (`.github/workflows/release.yml`)

Triggered on version tags (`v*`):

- Builds versioned Docker image
- Pushes to ghcr.io with semantic version tags
- Creates GitHub Release with auto-generated notes

## Technologies

| Category | Technology |
|----------|------------|
| Language | Python 3.11 |
| Framework | FastAPI |
| Testing | pytest, pytest-cov |
| Linting | Black, Ruff, Mypy |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry |
| Security | Trivy |

## License

MIT License - See [LICENSE](LICENSE) for details.
