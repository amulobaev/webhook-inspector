# Webhook Inspector

Real-time инструмент для отладки HTTP-запросов. Принимает **любые запросы** на `/hook/<path>`
и показывает их в браузере через WebSocket без перезагрузки страницы.

## Структура

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

## Быстрый запуск (без Traefik)

```bash
docker build -t webhook-inspector .
docker run -p 8000:8000 webhook-inspector
# Открой http://localhost:8000
```

## Деплой с Traefik

### 1. Создай внешнюю сеть (если нет)

```bash
docker network create traefik-public
```

### 2. Задай домен и запусти

```bash
echo "DOMAIN=webhook.yourdomain.com" > .env
docker compose up -d --build
```

### 3. Проверь

```bash
curl https://webhook.yourdomain.com/hook/test \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "value": 42}'
```

Запрос появится в браузере мгновенно.

## Предпосылки для Traefik

`docker-compose.yml` предполагает:
- entrypoints с именами `web` (80) и `websecure` (443)
- certresolver с именем `letsencrypt`
- `--providers.docker=true` и `--providers.docker.exposedByDefault=false`

## API

| Method | Path           | Description                              |
|--------|----------------|------------------------------------------|
| ANY    | `/hook/{path}` | Принимает любой запрос, сохраняет в памяти |
| GET    | `/`            | UI инспектора                            |
| WS     | `/ws`          | WebSocket для live-обновлений            |

> Хранит последние 100 запросов в памяти (сбрасывается при рестарте).
