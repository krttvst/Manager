# Deploy (Production)

This repo includes a production-ish docker compose setup with:
- Postgres + Redis
- FastAPI backend + Celery worker/beat
- Frontend served as a built SPA

Two deployment options are provided:
1) `docker-compose.prod.yml` with Caddy (automatic HTTPS). Requires ports 80/443 free on the host.
2) `docker-compose.nginx.prod.yml` for servers that already run host Nginx. Containers bind only to `127.0.0.1` and host Nginx proxies traffic.
3) (Recommended) Pull prebuilt images from GHCR and restart containers (no builds on server).

## Recommended: GHCR (pull images, no builds on server)
This repo publishes Docker images to GHCR on each push to `main` via GitHub Actions:
- `ghcr.io/krttvst/manager-tg-backend:<tag>`
- `ghcr.io/krttvst/manager-tg-frontend:<tag>`

Available tags include:
- `main` (branch tag)
- `<sha>` (short SHA tag)

### One-time server setup
1. Ensure `.env` exists on the server (do not commit it).
2. If GHCR packages are private, login once:
   - `docker login ghcr.io -u <github_user>`

### Deploy a new version
From the server project directory (e.g. `/root/manager-tg`):
```bash
export IMAGE_TAG=<sha>   # recommended for an exact version
./deploy/pull-up.sh
```

## Prerequisites
- A server with a public IPv4 address
- Docker + Docker Compose plugin installed
- DNS for your domain pointing to the server IP:
  - `A` record: `@` -> server IP
  - `A` record: `www` -> server IP (optional)
- Ports open: `80/tcp` and `443/tcp`

## 1) Prepare `.env` on the server
Create `.env` from `.env.example` and fill at least:
- `DOMAIN=example.com` (your domain)
- `ACME_EMAIL=you@example.com` (Let's Encrypt email)
- `APP_ENV=production`
- `APP_SECRET=<long random string>`
- `POSTGRES_PASSWORD=<strong password>`
- `DATABASE_URL=postgresql+psycopg://tg_admin:<same POSTGRES_PASSWORD>@db:5432/tg_manager`
- `ADMIN_PASSWORD=<strong password>`
- `TELEGRAM_BOT_TOKEN=<your bot token>`
- `N8N_API_KEY=<optional>`

## 2) Start services
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Alternative: host Nginx
If your server already runs Nginx on port 80/443, use:
```bash
docker compose -f docker-compose.nginx.prod.yml up -d --build
```
This starts:
- frontend on `127.0.0.1:18080`
- backend on `127.0.0.1:18000`

Then configure host Nginx to proxy:
- `/` -> `http://127.0.0.1:18080`
- `/v1/` and `/media/` -> `http://127.0.0.1:18000`

## 3) Apply migrations
```bash
docker compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head
```

## 4) Create admin user
```bash
docker compose -f docker-compose.prod.yml exec backend python -m app.scripts.create_admin
```

## Notes
- Caddy stores certificates in the `caddy_data` volume.
- Frontend/API are served from the same domain:
  - `/` -> frontend
  - `/v1/*` -> backend
  - `/media/*` -> backend static media
