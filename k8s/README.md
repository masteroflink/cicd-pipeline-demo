# Kubernetes Manifests

This directory contains Kubernetes manifests for deploying the CI/CD Demo application.

## Prerequisites

- Kubernetes cluster (1.26+)
- kubectl configured to access your cluster
- NGINX Ingress Controller (for ingress)
- cert-manager (for TLS certificates, optional)

## Manifests

| File | Description |
|------|-------------|
| `namespace.yaml` | Creates the `cicd-demo` namespace |
| `configmap.yaml` | Application configuration (environment variables) |
| `deployment.yaml` | Application deployment with 3 replicas |
| `service.yaml` | ClusterIP service for internal traffic |
| `ingress.yaml` | Ingress for external HTTP/HTTPS access |
| `hpa.yaml` | Horizontal Pod Autoscaler (3-10 pods) |

## Quick Start

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy all resources
kubectl apply -f k8s/

# Verify deployment
kubectl get all -n cicd-demo

# Check pod logs
kubectl logs -n cicd-demo -l app.kubernetes.io/name=cicd-demo -f
```

## Configuration

### Update Image

Replace `OWNER` in `deployment.yaml` with your GitHub username/organization:

```yaml
image: ghcr.io/YOUR-USERNAME/cicd-pipeline-demo:latest
```

### Update Ingress Host

Replace `api.example.com` in `ingress.yaml` with your domain:

```yaml
rules:
  - host: your-domain.com
```

### TLS Certificate

For production, configure cert-manager or provide a TLS secret:

```bash
kubectl create secret tls cicd-demo-tls \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem \
  -n cicd-demo
```

## Resource Configuration

### Deployment Resources

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 128Mi | 256Mi |

### HPA Configuration

| Setting | Value |
|---------|-------|
| Min Replicas | 3 |
| Max Replicas | 10 |
| CPU Target | 70% |
| Memory Target | 80% |
| Scale Down Window | 5 minutes |

## Health Checks

The deployment includes both liveness and readiness probes:

- **Liveness Probe**: `/health` endpoint, checks if the app is alive
- **Readiness Probe**: `/health` endpoint, checks if the app is ready to serve traffic

## Monitoring

Pods are annotated for Prometheus scraping:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

## Security

- Runs as non-root user (UID 1000)
- Read-only root filesystem
- All capabilities dropped
- No privilege escalation

## Scaling

Manual scaling:

```bash
kubectl scale deployment cicd-demo -n cicd-demo --replicas=5
```

HPA will automatically scale based on CPU and memory utilization.

## Troubleshooting

```bash
# Check pod status
kubectl get pods -n cicd-demo

# Describe failing pod
kubectl describe pod <pod-name> -n cicd-demo

# Check events
kubectl get events -n cicd-demo --sort-by='.lastTimestamp'

# Port forward for local testing
kubectl port-forward svc/cicd-demo 8000:80 -n cicd-demo
```
