# Architecture Documentation

## System Overview

This project demonstrates a production-ready CI/CD pipeline for a Python FastAPI application. The architecture follows modern DevOps best practices with containerization, automated testing, and continuous deployment.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GitHub Repository                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────────────────┐  │
│  │  main   │───▶│ develop │───▶│  tags   │    │   Pull Requests         │  │
│  └────┬────┘    └────┬────┘    └────┬────┘    └───────────┬─────────────┘  │
│       │              │              │                      │                │
└───────┼──────────────┼──────────────┼──────────────────────┼────────────────┘
        │              │              │                      │
        ▼              ▼              ▼                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                            GitHub Actions                                      │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────────────┐  │
│  │   CI Pipeline    │   │   CD Pipeline    │   │   Release Pipeline       │  │
│  ├──────────────────┤   ├──────────────────┤   ├──────────────────────────┤  │
│  │ 1. Lint          │   │ 1. Pull Image    │   │ 1. Build versioned image │  │
│  │ 2. Test          │   │ 2. Deploy        │   │ 2. Push to registry      │  │
│  │ 3. Build         │   │ 3. Smoke Test    │   │ 3. Create GH Release     │  │
│  │ 4. Push          │   │                  │   │                          │  │
│  │ 5. Security Scan │   │                  │   │                          │  │
│  └────────┬─────────┘   └────────┬─────────┘   └────────────┬─────────────┘  │
│           │                      │                          │                 │
└───────────┼──────────────────────┼──────────────────────────┼─────────────────┘
            │                      │                          │
            ▼                      ▼                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                      GitHub Container Registry (ghcr.io)                       │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │  ghcr.io/masteroflink/cicd-pipeline-demo                                  │ │
│  ├──────────────────────────────────────────────────────────────────────────┤ │
│  │  Tags: latest, v1.0.0, v1.0, v1, sha-abc123...                           │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Application Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FastAPI Application                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                              main.py                                    │ │
│  │                         FastAPI App Instance                            │ │
│  └─────────────────────────────────┬──────────────────────────────────────┘ │
│                                    │                                         │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          ▼                         ▼                         ▼              │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐       │
│  │   /health     │        │  /api/v1/     │        │  /api/v1/     │       │
│  │   endpoint    │        │    items      │        │   calculate   │       │
│  │   health.py   │        │   routes.py   │        │   routes.py   │       │
│  └───────────────┘        └───────┬───────┘        └───────┬───────┘       │
│                                   │                         │               │
│                                   ▼                         ▼               │
│                          ┌───────────────┐        ┌───────────────┐        │
│                          │    Pydantic   │        │   Calculator  │        │
│                          │    Models     │        │    Service    │        │
│                          │  schemas.py   │        │ calculator.py │        │
│                          └───────────────┘        └───────────────┘        │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                          In-Memory Storage                              │ │
│  │                          (Dict[str, Item])                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Docker Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Multi-Stage Build                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Stage 1: Builder                                                       │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │  python:3.11-slim                                                │   │ │
│  │  │  - Install build dependencies                                    │   │ │
│  │  │  - Create pip wheels                                             │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Stage 2: Production                                                    │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │  python:3.11-slim                                                │   │ │
│  │  │  - Copy wheels from builder                                      │   │ │
│  │  │  - Install from wheels (no build tools)                          │   │ │
│  │  │  - Non-root user (appuser)                                       │   │ │
│  │  │  - Health check configured                                       │   │ │
│  │  │  - Expose port 8000                                              │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Test-Driven Development (TDD)

All code is developed using TDD methodology:
- Write tests first (Red)
- Implement minimal code to pass (Green)
- Refactor while keeping tests green (Refactor)

This ensures 100% code coverage and reliable, well-designed code.

### 2. Multi-Stage Docker Builds

Using multi-stage builds provides:
- Smaller production images (no build tools)
- Faster deployments
- Reduced attack surface
- Cached dependency layers

### 3. Branch Strategy

- `main`: Production-ready code, full CI/CD pipeline
- `develop`: Integration branch, lint + test only
- Feature branches: Created from develop, merged via PR

### 4. Semantic Versioning

Releases follow semantic versioning (v1.0.0):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### 5. In-Memory Storage

Items API uses in-memory dictionary storage for simplicity:
- Resets on container restart
- Suitable for demonstration purposes
- Easy to swap for database in production

### 6. Security Best Practices

- Non-root container user
- Trivy vulnerability scanning
- Minimal base images
- No secrets in code or images

## Pipeline Stages

### Lint Stage
- **Black**: Code formatting check
- **Ruff**: Linting (replaces flake8, isort)
- **Mypy**: Static type checking

### Test Stage
- **pytest**: Test execution
- **pytest-cov**: Coverage reporting
- Artifacts: HTML coverage report

### Build Stage
- Docker multi-stage build
- Push to ghcr.io
- Tag with SHA and 'latest'

### Security Stage
- Trivy container scanning
- SARIF report upload
- Security tab integration

### Deploy Stage
- Pull from ghcr.io
- Simulate staging deployment
- Run smoke tests

## Environment Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| ENVIRONMENT | development | Current environment |
| LOG_LEVEL | INFO | Logging verbosity |
| PYTHONPATH | /app/src | Python module path |

## Scaling Considerations

For production scaling, consider:

1. **Database**: Replace in-memory storage with PostgreSQL/Redis
2. **Load Balancing**: Add nginx or cloud load balancer
3. **Caching**: Add Redis for session/response caching
4. **Monitoring**: Add Prometheus metrics and Grafana dashboards
5. **Logging**: Centralized logging with ELK or CloudWatch
