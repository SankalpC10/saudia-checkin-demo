# saudia-checkin-demo

Discardable demo repo for the Rtifact closing-the-loop prototype.

- `app/`: `checkin-service`, a FastAPI online check-in API with Prometheus metrics and JSON logs.
- `.github/workflows/ci.yml`: tests, then image pushed to GHCR, then the image tag is bumped in `deploy/`.
- `deploy/`: Kubernetes manifests that ArgoCD syncs (service plus a traffic generator).
- `argocd/application.yaml`: the ArgoCD Application that watches `deploy/` on `main`.
