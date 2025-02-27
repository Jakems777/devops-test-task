## 1. System Requirements

### CPU & Memory Estimations
| Component        | CPU       | Memory   | Disk    | Description               |
|----------------|----------|---------|-------|---------------------------|
| Flask App      | 0.3 vCPU | 150MB   | -     | Python flask  |
| Grafana Alloy  | 0.8 vCPU | 800MB   | 200MB | otlp receiver and loki writer |
| Grafana Loki   | 0.7 vCPU | 1GB     | 2GB/day | Log storage backend  |
| Grafana        | 0.4 vCPU | 400MB   | 100MB | Visualizing logs loki datasource |
| **Total**      | **2.2 vCPU** | **2.35GB RAM** | **2GB/day Disk** | Observability stack |


If traffic grows and amount of apps grow and system scales, consider deploying Alloy as a sidecar container alongside each app/service. Loki can be scaled horizontally by sharding log streams and retention policy adjusted per requirements. Grafana 1-3 instances as centralised service.

---

## 2. Deployment manual

### Prerequisites
- Docker
- Docker Compose
- Linux/macOS (I tried at home windows pc and struggled, so windows out of scope)

### How to Deploy
1. Clone the repository:
```bash
git clone 
cd to root
```

2. Lets go:
```bash
docker compose up -d --build
```

3. Verify the services:
- Grafana: http://localhost:3000
- Alloy UI: http://localhost:12345
- Flask App: http://localhost:8080
- Loki http://localhost:3100/ready

## 3. Testing manual:
- docker desktop is handy at checking your containers make sure they up and running
- curl or postman or browser localhost:3000/health or /post or /get for py app
- open alloy ui debugging at localhost:12345/debug/otelcol.receiver.otlp.default and check for incoming data
- check that loki persisted the logs by sh-ing into the container and exahmine chunks dir or run a loki query:

```
curl -G -u admin:admin \
"http://localhost:3100/loki/api/v1/query_range" \
--data-urlencode 'query={service_name="flask-dummy"}' \
--data-urlencode 'start=2025-02-27T00:00:00Z' \
--data-urlencode 'end=2025-02-28T00:00:00Z' \
--data-urlencode 'limit=10'
```

if you got a json response then you are gucci, if not then check loki official docs or make sure you troubleshoot the whole chain of components starting from py app. 

- navigate to loki datasources in grafana and query the flask-dummy to see the logs in grafana ui

## 4. Service Diagram:
```plaintext

[ Flask App ]
     ↓ OTLP Logs (gRPC)
[ Grafana Alloy ]
     ├─ Receives via otelcol.receiver.otlp
     ├─ Processes via otelcol.processor.attributes
     └─ Exports to Loki via otelcol.exporter.loki
           ↓
[ Loki ]
     └─ Stores logs + exposes API
           ↓
[ Grafana ]
     └─ Visualizes logs
```

