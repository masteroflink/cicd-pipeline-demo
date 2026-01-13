#!/usr/bin/env bash
#
# Minikube Teardown Script for CI/CD Pipeline Demo
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
KUBECTL="kubectl"  # May be overridden to "minikube kubectl --" if standalone kubectl not found

# Detect kubectl
if command -v kubectl &> /dev/null; then
    KUBECTL="kubectl"
elif minikube kubectl -- version --client &>/dev/null 2>&1; then
    KUBECTL="minikube kubectl --"
fi

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

uninstall_helm_release() {
    log_info "Checking for Helm release..."

    if helm status "$RELEASE_NAME" --namespace "$NAMESPACE" &>/dev/null; then
        log_info "Uninstalling Helm release '$RELEASE_NAME'..."
        helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE"
        log_success "Helm release uninstalled"
    else
        log_warn "Helm release '$RELEASE_NAME' not found (already removed)"
    fi
}

delete_namespace() {
    log_info "Checking for namespace..."

    if $KUBECTL get namespace "$NAMESPACE" &>/dev/null; then
        log_info "Deleting namespace '$NAMESPACE'..."
        $KUBECTL delete namespace "$NAMESPACE"
        log_success "Namespace deleted"
    else
        log_warn "Namespace '$NAMESPACE' not found (already removed)"
    fi
}

print_status() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}Teardown Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "The CI/CD demo has been removed from Minikube."
    echo ""
    echo "Minikube is still running. To stop it:"
    echo "  minikube stop"
    echo ""
    echo "To delete Minikube entirely:"
    echo "  minikube delete"
    echo ""
    echo "To redeploy:"
    echo "  ./scripts/minikube-setup.sh"
    echo ""
}

main() {
    echo ""
    echo "=========================================="
    echo "  CI/CD Pipeline Demo - Minikube Teardown"
    echo "=========================================="
    echo ""

    # Check if minikube is running
    if ! minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
        log_warn "Minikube is not running, nothing to teardown"
        exit 0
    fi

    uninstall_helm_release
    delete_namespace
    print_status
}

main "$@"
