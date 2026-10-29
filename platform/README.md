# Local platform

Everything the prototype needs besides the app itself. It all runs on one laptop.

```
kind cluster "rtifact"                         host (Docker)
├── argocd/          syncs deploy/ from GitHub
├── checkin/         checkin-service + traffic generator
└── observability/
    ├── vmagent  ── scrapes annotated pods ──▶  VictoriaMetrics :8428 ◀── vmalert :8880
    └── vector   ── ships checkin logs ──────▶  VictoriaLogs    :9428        │ HighErrorRate
                                                                              ▼
                     proactive agent :8002  ◀── reads VM + VL ───  alert webhook
                     anomaly scorer  :8090  ── writes anomaly_score to VM
```

## Start

```bash
# 1. Metrics, logs and alert rules on the host
docker compose -f platform/docker-compose.yml up -d

# 2. Scraper and log shipper inside kind
kubectl apply --context kind-rtifact -f platform/kind/

# 3. Proactive agent (host port 8002) and anomaly scorer (8090)
platform/proactive/up.sh
```

`up.sh` overlays `platform/proactive/compose.override.yml` on the `rt-ai-proactive-monitoring`
compose file (set `PROACTIVE_REPO` if that repo is not in `~/PycharmProjects`). The overlay:
- points both services at the host VictoriaMetrics and VictoriaLogs,
- mounts `tenants.yaml` (tenant `saudia-demo`, service `checkin-service`), so no MongoDB provisioning record is needed,
- shrinks scorer training to a 3-hour window with 30 points, so it can train after about 30 minutes of healthy traffic.

## Check it

```bash
# Request rate by status
curl -s localhost:8428/api/v1/query \
  --data-urlencode 'query=sum by (status) (rate(http_requests_total{service_name="checkin-service"}[2m]))'

# Latest application log
curl -s localhost:9428/select/logsql/query \
  --data-urlencode 'query=rtf_service:"checkin-service" level:info | limit 1'

# Agent view of the service (connectivity, label mapping, log samples)
curl -s "localhost:8002/proactive-anomaly/tenants/0/0/diagnostic/checkin-service?window=15m" | jq .connectivity

# Scorer state (phase 0 = cold start, still collecting baseline)
curl -s localhost:8090/models
```

## Labels that must line up

| Where | Field | Value |
|---|---|---|
| App metrics | `service_name` | `checkin-service` |
| Logs (set by vector) | `rtf_service`, `kubernetes.pod_labels.app` | `checkin-service` |
| Logs (set by vector) | `rtf_tenant_id` | `saudia-demo` |
| Agent tenant | `services` in `tenants.yaml` | `checkin-service` |
