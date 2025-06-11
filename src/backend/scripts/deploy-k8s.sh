#!/bin/bash
set -e

# Kubernetes deployment script for GTD Backend

# Configuration
NAMESPACE="gtd-system"
KUBECTL_CONTEXT=${KUBECTL_CONTEXT:-""}
DRY_RUN=${DRY_RUN:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    if [ -n "$KUBECTL_CONTEXT" ]; then
        log_info "Using kubectl context: $KUBECTL_CONTEXT"
        kubectl config use-context "$KUBECTL_CONTEXT"
    fi
    
    log_info "Current kubectl context: $(kubectl config current-context)"
}

# Create namespace
create_namespace() {
    log_info "Creating namespace..."
    if $DRY_RUN; then
        kubectl apply -f k8s/namespace.yaml --dry-run=client
    else
        kubectl apply -f k8s/namespace.yaml
    fi
}

# Deploy secrets (you need to create these manually first)
deploy_secrets() {
    log_warn "Please ensure secrets are created manually before deployment:"
    echo "kubectl create secret generic gtd-backend-secrets \\"
    echo "  --from-literal=POSTGRES_URL=\"postgresql+asyncpg://user:password@host:5432/database\" \\"
    echo "  --from-literal=SUPABASE_URL=\"https://your-project.supabase.co\" \\"
    echo "  --from-literal=SUPABASE_SERVICE_ROLE_KEY=\"your-service-role-key\" \\"
    echo "  --from-literal=SECRET_KEY=\"your-very-long-secret-key-here\" \\"
    echo "  --namespace=$NAMESPACE"
    echo ""
    read -p "Have you created the secrets? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Please create secrets first"
        exit 1
    fi
}

# Deploy application
deploy_app() {
    log_info "Deploying application..."
    
    local files=(
        "k8s/configmap.yaml"
        "k8s/deployment.yaml"
        "k8s/service.yaml"
        "k8s/ingress.yaml"
        "k8s/hpa.yaml"
        "k8s/networkpolicy.yaml"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            log_info "Applying $file..."
            if $DRY_RUN; then
                kubectl apply -f "$file" --dry-run=client
            else
                kubectl apply -f "$file"
            fi
        else
            log_warn "File $file not found, skipping..."
        fi
    done
}

# Wait for deployment
wait_for_deployment() {
    if $DRY_RUN; then
        log_info "Dry run mode, skipping wait..."
        return
    fi
    
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/gtd-backend -n "$NAMESPACE"
    
    log_info "Checking pod status..."
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=gtd-backend
}

# Show deployment status
show_status() {
    if $DRY_RUN; then
        return
    fi
    
    log_info "Deployment status:"
    kubectl get all -n "$NAMESPACE"
    
    log_info "Service endpoints:"
    kubectl get ingress -n "$NAMESPACE"
    
    log_info "Recent events:"
    kubectl get events -n "$NAMESPACE" --sort-by='.metadata.creationTimestamp' | tail -10
}

# Main deployment flow
main() {
    log_info "Starting GTD Backend deployment to Kubernetes..."
    
    # Change to script directory
    cd "$(dirname "$0")/.."
    
    check_prerequisites
    create_namespace
    deploy_secrets
    deploy_app
    wait_for_deployment
    show_status
    
    log_info "Deployment completed successfully!"
    log_info "You can check the application at: kubectl get ingress -n $NAMESPACE"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --context)
            KUBECTL_CONTEXT="$2"
            shift 2
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --dry-run        Run in dry-run mode"
            echo "  --context CTX    Use specific kubectl context"
            echo "  --namespace NS   Use specific namespace (default: gtd-system)"
            echo "  -h, --help       Show this help"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main