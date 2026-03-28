# Webhook Inspector

Real-time tool for debugging HTTP requests. Accepts **any requests** on `/hook/<path>`
and displays them in the browser via WebSocket without page reload.

## Structure

```
webhook-inspector/
├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
├── Dockerfile
├── docker-compose.yml
└── .env
```

## Quick Start (without Traefik)

```bash
docker build -t webhook-inspector .
docker run -p 8000:8000 webhook-inspector
# Open http://localhost:8000
```

## Deploy with Traefik

### 1. Create external network (if not exists)

```bash
docker network create traefik-public
```

### 2. Set domain and run

```bash
echo "DOMAIN=webhook.yourdomain.com" > .env
docker compose up -d --build
```

### 3. Verify

```bash
curl https://webhook.yourdomain.com/hook/test \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "value": 42}'
```

The request will appear in the browser instantly.

## Traefik Prerequisites

`docker-compose.yml` assumes:
- entrypoints named `web` (80) and `websecure` (443)
- certresolver named `letsencrypt`
- `--providers.docker=true` and `--providers.docker.exposedByDefault=false`

## API

| Method | Path           | Description                              |
|--------|----------------|------------------------------------------|
| ANY    | `/hook/{path}` | Accepts any request, stores in memory    |
| GET    | `/`            | Inspector UI                             |
| WS     | `/ws`          | WebSocket for live updates               |

> Stores the last 100 requests in memory (cleared on restart).
