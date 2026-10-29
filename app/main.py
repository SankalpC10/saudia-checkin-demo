"""checkin-service: online check-in API for the Rtifact demo."""
import json
import logging
import os
import sys
import time
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.bookings import get_booking
from app.checkin import boarding_pass

SERVICE = os.getenv("SERVICE_NAME", "checkin-service")
VERSION = os.getenv("APP_VERSION", "dev")

REQUESTS = Counter("http_requests_total", "HTTP requests", ["service_name", "method", "route", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["service_name", "route"])


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname.lower(),
            "service": SERVICE,
            "version": VERSION,
            "msg": record.getMessage(),
        }
        entry.update(getattr(record, "extra_fields", {}))
        if record.exc_info:
            entry["error"] = "".join(traceback.format_exception(*record.exc_info))
        return json.dumps(entry)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
log = logging.getLogger(SERVICE)
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = False

app = FastAPI(title="checkin-service")


@app.middleware("http")
async def observe(request: Request, call_next):
    route = request.scope.get("route")
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        log.error("unhandled error", exc_info=True, extra={"extra_fields": {"path": request.url.path}})
        response = JSONResponse({"detail": "internal error"}, status_code=500)
    route = request.scope.get("route")
    label = route.path if route else request.url.path
    if label != "/metrics":
        REQUESTS.labels(SERVICE, request.method, label, str(response.status_code)).inc()
        LATENCY.labels(SERVICE, label).observe(time.perf_counter() - start)
    return response


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/checkin/{pnr}")
def checkin(pnr: str):
    result = boarding_pass(get_booking(pnr))
    log.info("checked in", extra={"extra_fields": {"pnr": result["pnr"], "route": result["route"]}})
    return result
