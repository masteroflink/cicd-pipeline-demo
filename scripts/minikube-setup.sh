#!/usr/bin/env bash
#
# Minikube Setup Script for CI/CD Pipeline Demo
# This script is idempotent - safe to run multiple times
#
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="cicd-demo"
RELEASE_NAME="cicd-demo"
IMAGE_NAME="cicd-demo"
IMAGE_TAG="latest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KUBECTL="kubectl"  # May be overridden to "minikube kubectl --" if standalone kubectl not found

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=()

    if ! command -v minikube &> /dev/null; then
        missing+=("minikube")
    fi

    # kubectl can be standalone or provided by minikube
    if command -v kubectl &> /dev/null; then
        KUBECTL="kubectl"
    elif minikube kubectl -- version --client &>/dev/null; then
        KUBECTL="minikube kubectl --"
        log_info "Using minikube's built-in kubectl"
    else
        missing+=("kubectl")
    fi

    if ! command -v helm &> /dev/null; then
        missing+=("helm")
    fi

    if ! command -v docker &> /dev/null; then
        missing+=("docker")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing[*]}"
        echo "Please install the missing tools and try again."
        exit 1
    fi

    log_success "All prerequisites installed"
}

ensure_minikube_running() {
    log_info "Checking Minikube status..."

    if minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
        log_success "Minikube is already running"
    else
        log_info "Starting Minikube..."
        minikube start --memory=4096 --cpus=2
        log_success "Minikube started"
    fi
}

enable_addons() {
    log_info "Enabling required addons..."

    # Enable ingress addon
    if minikube addons list | grep -E "ingress\s*\|\s*enabled" &>/dev/null; then
        log_success "Ingress addon already enabled"
    else
        log_info "Enabling ingress addon..."
        minikube addons enable ingress
        log_success "Ingress addon enabled"
    fi

    # Enable metrics-server addon (required for HPA)
    if minikube addons list | grep -E "metrics-server\s*\|\s*enabled" &>/dev/null; then
        log_success "Metrics-server addon already enabled"
    else
        log_info "Enabling metrics-server addon..."
        minikube addons enable metrics-server
        log_success "Metrics-server addon enabled"
    fi
}

build_docker_image() {
    log_info "Building Docker image in Minikube..."

    # Switch to Minikube's Docker daemon
    eval $(minikube docker-env)

    # Build the image
    docker build \
        -t "${IMAGE_NAME}:${IMAGE_TAG}" \
        -f "${PROJECT_ROOT}/docker/Dockerfile" \
        "${PROJECT_ROOT}"

    log_success "Docker image built: ${IMAGE_NAME}:${IMAGE_TAG}"
}

create_namespace() {
    log_info "Ensuring namespace exists..."

    if $KUBECTL get namespace "$NAMESPACE" &>/dev/null; then
        log_success "Namespace '$NAMESPACE' already exists"
    else
        $KUBECTL create namespace "$NAMESPACE"
        log_success "Namespace '$NAMESPACE' created"
    fi
}

update_helm_dependencies() {
    log_info "Updating Helm chart dependencies..."

    local chart_path="${PROJECT_ROOT}/helm/cicd-demo"

    helm dependency update "$chart_path"

    log_success "Helm dependencies updated"
}

deploy_helm_chart() {
    log_info "Deploying with Helm..."

    local values_file="${PROJECT_ROOT}/helm/cicd-demo/values-minikube.yaml"
    local chart_path="${PROJECT_ROOT}/helm/cicd-demo"

    # Use upgrade --install for idempotent deployment
    helm upgrade --install "$RELEASE_NAME" "$chart_path" \
        --namespace "$NAMESPACE" \
        --values "$values_file" \
        --wait \
        --timeout 8m

    log_success "Helm release '$RELEASE_NAME' deployed"
}

wait_for_database() {
    log_info "Waiting for PostgreSQL to be ready..."

    $KUBECTL wait --namespace "$NAMESPACE" \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/name=postgresql \
        --timeout=120s 2>/dev/null || {
        log_warn "PostgreSQL pod not found or not ready, continuing..."
        return 0
    }

    log_success "PostgreSQL is ready"
}

wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."

    $KUBECTL rollout status deployment/"$RELEASE_NAME" \
        --namespace "$NAMESPACE" \
        --timeout=120s

    log_success "Deployment is ready"
}

wait_for_ingress() {
    log_info "Waiting for ingress controller to be ready..."

    # Wait for ingress controller pod
    $KUBECTL wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s 2>/dev/null || {
        log_warn "Ingress controller not ready yet, continuing..."
    }

    # Give ingress a moment to configure
    sleep 5

    log_success "Ingress controller is ready"
}

print_access_info() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "Access the application:"
    echo ""
    echo "  Option 1: Use minikube tunnel (recommended)"
    echo "    Run in a separate terminal:"
    echo -e "    ${YELLOW}sudo minikube tunnel${NC}"
    echo ""
    echo "    Then access: http://localhost/health"
    echo ""
    echo "  Option 2: Use port-forward"
    echo -e "    ${YELLOW}kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME 8000:80${NC}"
    echo ""
    echo "    Then access: http://localhost:8000/health"
    echo ""
    echo "Test the API:"
    echo "  curl http://localhost/health"
    echo "  curl http://localhost/api/v1/items"
    echo ""
    echo "Test autoscaling:"
    echo "  # Generate load (install hey: go install github.com/rakyll/hey@latest)"
    echo "  hey -n 5000 -c 50 http://localhost/api/v1/items"
    echo ""
    echo "  # Watch HPA and pods"
    echo "  kubectl get hpa,pods -n $NAMESPACE -w"
    echo ""
    echo "View logs:"
    echo "  kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=$RELEASE_NAME -f"
    echo ""
    echo "Teardown:"
    echo "  ./scripts/minikube-teardown.sh"
    echo ""
}

main() {
    echo ""
    echo "=========================================="
    echo "  CI/CD Pipeline Demo - Minikube Setup"
    echo "=========================================="
    echo ""

    check_prerequisites
    ensure_minikube_running
    enable_addons
    build_docker_image
    create_namespace
    update_helm_dependencies
    deploy_helm_chart
    wait_for_database
    wait_for_deployment
    wait_for_ingress
    print_access_info
}

main "$@"
