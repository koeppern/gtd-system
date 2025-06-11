# GTD Backend Deployment Guide

Dieses Dokument beschreibt, wie du das GTD Backend als Docker Container und auf Kubernetes deployest.

## Voraussetzungen

### Allgemein
- Docker 20.10+
- Git
- Ein gültiger Datenbankzugang (PostgreSQL oder Supabase)

### Für Kubernetes
- kubectl
- Zugang zu einem Kubernetes Cluster
- Ingress Controller (z.B. nginx-ingress oder Traefik)
- Optional: cert-manager für TLS-Zertifikate
- Optional: Metrics Server für HPA

## Docker Deployment

### 1. Image erstellen

```bash
# Einfacher Build
./scripts/build-docker.sh

# Mit spezifischem Tag
./scripts/build-docker.sh v1.0.0

# Für Registry
DOCKER_REGISTRY=your-registry.com ./scripts/build-docker.sh v1.0.0
```

### 2. Docker Compose (Lokale Entwicklung)

```bash
# Umgebungsvariablen setzen
cp .env.example .env
# Bearbeite .env mit deinen Datenbankdaten

# Starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f gtd-backend

# Stoppen
docker-compose down
```

### 3. Standalone Docker Container

```bash
# Container starten
docker run -d \
  --name gtd-backend \
  -p 8000:8000 \
  -e POSTGRES_URL="postgresql+asyncpg://user:password@host:5432/database" \
  -e SECRET_KEY="your-secret-key" \
  -v /path/to/config:/app/config:ro \
  gtd-backend:latest

# Logs anzeigen
docker logs -f gtd-backend

# Health Check
curl http://localhost:8000/health
```

## Kubernetes Deployment

### 1. Vorbereitung

#### Secrets erstellen
```bash
# Hauptsecrets
kubectl create secret generic gtd-backend-secrets \
  --from-literal=POSTGRES_URL="postgresql+asyncpg://user:password@host:5432/database" \
  --from-literal=SUPABASE_URL="https://your-project.supabase.co" \
  --from-literal=SUPABASE_SERVICE_ROLE_KEY="your-service-role-key" \
  --from-literal=SECRET_KEY="your-very-long-secret-key-here" \
  --namespace=gtd-system
```

#### Image in Registry pushen
```bash
# Image taggen und pushen
docker tag gtd-backend:latest your-registry.com/gtd-backend:latest
docker push your-registry.com/gtd-backend:latest

# Deployment manifest aktualisieren
# Ändere 'image: gtd-backend:latest' in k8s/deployment.yaml
```

### 2. Automatisches Deployment

```bash
# Vollständiges Deployment
./scripts/deploy-k8s.sh

# Dry-run zum Testen
./scripts/deploy-k8s.sh --dry-run

# Mit spezifischem Context
./scripts/deploy-k8s.sh --context my-cluster-context
```

### 3. Manuelles Deployment

```bash
# Namespace erstellen
kubectl apply -f k8s/namespace.yaml

# ConfigMap und Secrets
kubectl apply -f k8s/configmap.yaml
# Secrets müssen manuell erstellt werden (siehe oben)

# Application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Optional: Auto-scaling und Netzwerk-Policies
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/networkpolicy.yaml
```

### 4. Deployment überprüfen

```bash
# Status anzeigen
kubectl get all -n gtd-system

# Pod-Logs
kubectl logs -f deployment/gtd-backend -n gtd-system

# Service endpoints
kubectl get ingress -n gtd-system

# Health Check
kubectl port-forward service/gtd-backend-service 8000:80 -n gtd-system
curl http://localhost:8000/health
```

## Konfiguration

### Umgebungsvariablen

| Variable | Beschreibung | Erforderlich |
|----------|--------------|--------------|
| `CONFIG_FILE` | Pfad zur Konfigurationsdatei | Nein (Standard: config.yaml) |
| `POSTGRES_URL` | PostgreSQL Verbindungsstring | Ja* |
| `SUPABASE_URL` | Supabase Projekt URL | Ja* |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key | Ja* |
| `SECRET_KEY` | JWT Secret Key (min. 32 Zeichen) | Ja |

*Entweder PostgreSQL oder Supabase

### Konfigurationsdateien

- `config/config.yaml` - Entwicklung
- `config/production.yaml` - Produktion
- `config/test_config.yaml` - Tests

## Monitoring und Logging

### Health Checks
- Endpoint: `GET /health`
- Liveliness: Alle 30s
- Readiness: Alle 10s

### Logs
```bash
# Docker
docker logs gtd-backend

# Kubernetes
kubectl logs -f deployment/gtd-backend -n gtd-system

# Mit stern (mehrere Pods)
stern gtd-backend -n gtd-system
```

### Metrics
- Prometheus Metrics: `/metrics` (wenn aktiviert)
- Health Status: `/health`

## Sicherheit

### Docker
- Non-root User (UID 1000)
- Read-only root filesystem
- Minimales base image
- Security scanning mit Trivy

### Kubernetes
- Security Context
- Network Policies
- Resource Limits
- Non-root containers
- Service Account ohne Token

## Fehlerbehebung

### Häufige Probleme

#### 1. Database Connection Failed
```bash
# Check database accessibility
kubectl exec -it deployment/gtd-backend -n gtd-system -- python -c "
import asyncio
from app.database import async_session_maker
async def test():
    async with async_session_maker() as session:
        await session.execute('SELECT 1')
    print('DB OK')
asyncio.run(test())
"
```

#### 2. Config File Not Found
```bash
# Check config mount
kubectl exec -it deployment/gtd-backend -n gtd-system -- ls -la /app/config/
kubectl describe configmap gtd-backend-config -n gtd-system
```

#### 3. Image Pull Errors
```bash
# Check image and secrets
kubectl describe pod -l app.kubernetes.io/name=gtd-backend -n gtd-system
kubectl get imagepullsecrets -n gtd-system
```

#### 4. Ingress nicht erreichbar
```bash
# Check ingress controller
kubectl get ingressclass
kubectl get ingress -n gtd-system
kubectl describe ingress gtd-backend-ingress -n gtd-system

# Check DNS
nslookup gtd-api.your-domain.com
```

### Debug Commands

```bash
# Pod Shell
kubectl exec -it deployment/gtd-backend -n gtd-system -- /bin/bash

# Port Forward für lokalen Zugriff
kubectl port-forward service/gtd-backend-service 8000:80 -n gtd-system

# Events anzeigen
kubectl get events -n gtd-system --sort-by='.metadata.creationTimestamp'

# Resource Usage
kubectl top pods -n gtd-system
kubectl describe hpa gtd-backend-hpa -n gtd-system
```

## Updates und Rollbacks

### Rolling Update
```bash
# Image Update
kubectl set image deployment/gtd-backend gtd-backend=your-registry.com/gtd-backend:v1.1.0 -n gtd-system

# Update Status
kubectl rollout status deployment/gtd-backend -n gtd-system

# Rollback
kubectl rollout undo deployment/gtd-backend -n gtd-system

# History
kubectl rollout history deployment/gtd-backend -n gtd-system
```

### Zero-Downtime Deployment
- Konfigurierte Health Checks
- Rolling Update Strategy
- Min 2 Replicas
- Proper Grace Periods

## Performance Tuning

### Resource Requests/Limits
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Horizontal Pod Autoscaler
- CPU Threshold: 70%
- Memory Threshold: 80%
- Min Replicas: 2
- Max Replicas: 10

### Database Connections
- Connection pooling in FastAPI
- Async connections für bessere Performance
- Timeout-Konfiguration

## Backup und Disaster Recovery

### Database Backups
- Regelmäßige PostgreSQL/Supabase Backups
- Point-in-time Recovery
- Cross-region Replikation

### Application State
- Stateless Application Design
- Externe Session Storage (Redis)
- Configuration in ConfigMaps/Secrets

## Support und Kontakt

Bei Problemen:
1. Logs überprüfen
2. Health Checks testen
3. Database Connectivity prüfen
4. Kubernetes Events analysieren

Für weitere Hilfe siehe Repository Issues oder Dokumentation.