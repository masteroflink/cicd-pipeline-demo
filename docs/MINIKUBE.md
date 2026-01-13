# Running in Minikube

This guide covers running the CI/CD Pipeline Demo locally using Minikube.

## Prerequisites

Install the following tools:

- [Minikube](https://minikube.sigs.k8s.io/docs/start/) - Local Kubernetes cluster
- [kubectl](https://kubernetes.io/docs/tasks/tools/) - Kubernetes CLI
- [Helm](https://helm.sh/docs/intro/install/) - Kubernetes package manager
- [Docker](https://docs.docker.com/get-docker/) - Container runtime

Verify installation:

```bash
minikube version
kubectl version --client
helm version
docker --version
```

## Quick Start

Run the setup script:

```bash
./scripts/minikube-setup.sh
```

This will:
1. Start Minikube (if not running)
2. Enable ingress and metrics-server addons
3. Build the Docker image locally
4. Deploy the application with Helm
5. Print access instructions

## Accessing the Application

### Option 1: Minikube Tunnel (Recommended)

Run in a separate terminal:

```bash
sudo minikube tunnel
```

Then access the app at:
- Health check: http://localhost/health
- API: http://localhost/api/v1/items

### Option 2: Port Forward

```bash
kubectl port-forward -n cicd-demo svc/cicd-demo 8000:80
```

Then access at http://localhost:8000

## Testing Autoscaling

The Minikube setup includes HPA (Horizontal Pod Autoscaler) configured for local testing.

### Generate Load

Install [hey](https://github.com/rakyll/hey) load testing tool:

```bash
go install github.com/rakyll/hey@latest
```

Generate load to trigger scaling:

```bash
hey -n 5000 -c 50 http://localhost/api/v1/items
```

### Watch Scaling

In another terminal, watch the HPA and pods:

```bash
kubectl get hpa,pods -n cicd-demo -w
```

You should see:
1. HPA reporting increased CPU usage
2. New pods being created (up to 3 max)
3. Pods scaling back down after load stops

### HPA Configuration

| Setting | Minikube | Production |
|---------|----------|------------|
| Min Replicas | 1 | 3 |
| Max Replicas | 3 | 10 |
| CPU Target | 50% | 70% |

The lower CPU target (50%) makes it easier to trigger scaling during testing.

## Rebuilding After Code Changes

After modifying application code:

```bash
# Re-run the setup script (idempotent)
./scripts/minikube-setup.sh
```

Or manually rebuild:

```bash
# Switch to Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild the image
docker build -t cicd-demo:latest -f docker/Dockerfile .

# Restart the deployment to pick up the new image
kubectl rollout restart deployment/cicd-demo -n cicd-demo
```

## Useful Commands

```bash
# View pods
kubectl get pods -n cicd-demo

# View logs
kubectl logs -n cicd-demo -l app.kubernetes.io/name=cicd-demo -f

# Describe deployment
kubectl describe deployment cicd-demo -n cicd-demo

# View HPA status
kubectl get hpa -n cicd-demo

# View ingress
kubectl get ingress -n cicd-demo

# Shell into a pod
kubectl exec -it -n cicd-demo deploy/cicd-demo -- /bin/sh

# View all resources
kubectl get all -n cicd-demo
```

## Teardown

Remove the application from Minikube:

```bash
./scripts/minikube-teardown.sh
```

This removes the Helm release and namespace but keeps Minikube running.

To stop Minikube:

```bash
minikube stop
```

To delete Minikube entirely:

```bash
minikube delete
```

## Troubleshooting

### Pods stuck in Pending

Check events for scheduling issues:

```bash
kubectl describe pod -n cicd-demo
```

Common causes:
- Insufficient resources (increase Minikube memory/CPU)
- Image pull errors (ensure image was built with Minikube's Docker)

### Ingress not working

1. Verify ingress addon is enabled:
   ```bash
   minikube addons list | grep ingress
   ```

2. Check ingress controller is running:
   ```bash
   kubectl get pods -n ingress-nginx
   ```

3. Ensure `minikube tunnel` is running (requires sudo)

### HPA shows "unknown" metrics

Enable metrics-server addon:

```bash
minikube addons enable metrics-server
```

Wait a minute for metrics to be collected:

```bash
kubectl top pods -n cicd-demo
```

### Image pull errors

Ensure you're using Minikube's Docker daemon:

```bash
eval $(minikube docker-env)
docker images | grep cicd-demo
```

If the image isn't listed, rebuild it:

```bash
docker build -t cicd-demo:latest -f docker/Dockerfile .
```

### Connection refused

1. Check pods are running:
   ```bash
   kubectl get pods -n cicd-demo
   ```

2. Check service endpoints:
   ```bash
   kubectl get endpoints -n cicd-demo
   ```

3. Try port-forward directly:
   ```bash
   kubectl port-forward -n cicd-demo svc/cicd-demo 8000:80
   curl http://localhost:8000/health
   ```

## Differences from Production

| Aspect | Minikube | Production |
|--------|----------|------------|
| Replicas | 1 (HPA: 1-3) | 3 (HPA: 3-10) |
| Image Source | Local build | ghcr.io |
| Ingress Host | localhost | api.example.com |
| TLS | Disabled | Enabled |
| Pod Anti-Affinity | Disabled | Required |
| Resources | 100m/128Mi | 500m/256Mi |
| Log Level | DEBUG | INFO |

These differences optimize for local development while production values ensure high availability and security.
