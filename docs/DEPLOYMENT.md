# SentinelAI Production Deployment & DevOps Guide

This document covers enterprise production deployment strategies for SentinelAI using Docker Compose, PostgreSQL 16, Redis 7, Nginx Reverse Proxy, and SSL/TLS security configuration.

---

## 1. Production Architecture Topology

```
                   Internet / Security Operations Center (SOC)
                                        |
                                  HTTPS (Port 443)
                                        |
                              +---------v---------+
                              |   Nginx Gateway   |
                              |  (Docker: Port 80)|
                              +----+---------+----+
                                   |         |
                      /api & /ws   |         |  Static Assets
                                   v         v
                      +------------+----+  +-+-----------------+
                      | FastAPI Backend |  | React SPA Build   |
                      | (Port 8000)     |  | (/usr/share/html) |
                      +----+-------+----+  +-------------------+
                           |       |
                           v       v
                     +-----+---+ +-+-------+
                     |Postgres | | Redis 7 |
                     | (5432)  | |  (6379) |
                     +---------+ +---------+
```

---

## 2. Docker Compose Production Configuration

The `docker/docker-compose.yml` orchestrates 4 core containers:
1. `postgres`: Managed PostgreSQL 16 database storing user accounts, incident history, and audit logs.
2. `redis`: High-speed Redis 7 cache for token revocation and live stream telemetry.
3. `backend`: Scalable FastAPI container with Uvicorn worker pool.
4. `frontend`: Nginx Alpine container serving compressed Vite bundle.

### Deploying the Stack:
```bash
docker-compose -f docker/docker-compose.yml up -d --build
```

---

## 3. SSL / HTTPS Security Configuration (Let's Encrypt / Certbot)

For production deployments, terminate SSL at Nginx:

1. Install Certbot:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. Generate Certificates:
```bash
sudo certbot --nginx -d sentinelai.yourdomain.com
```

3. Update `docker/nginx.conf` with SSL certificate paths:
```nginx
server {
    listen 443 ssl http2;
    server_name sentinelai.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/sentinelai.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sentinelai.yourdomain.com/privkey.pem;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 4. Monitoring & Backup Procedures

### Database Backup (PostgreSQL):
```bash
docker exec -t sentinel_postgres pg_dump -U sentinel_admin sentinelai_db > sentinelai_backup_$(date +%Y%m%d).sql
```

### Log Inspection:
```bash
docker-compose -f docker/docker-compose.yml logs -f backend
```
