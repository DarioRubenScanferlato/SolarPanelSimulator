# Deployment Guide

This guide covers production deployment of the Solar Panel Simulator with HTTPS via nginx and Let's Encrypt.

---

## 1. Prerequisites

**Server requirements:**
- Ubuntu 22.04 LTS (or any Linux with systemd)
- 1 GB RAM minimum, 2 GB recommended
- Ports 80 and 443 open in firewall
- Docker Engine 24+ and Docker Compose v2+

**Domain:**
- A registered domain pointing to the server's public IP (e.g. `solar.yourdomain.com`)
- DNS A record must propagate before running certbot

**Install Docker on Ubuntu:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

---

## 2. DNS Setup

Create an A record for your domain:

| Type | Name                  | Value           | TTL  |
|------|-----------------------|-----------------|------|
| A    | solar.yourdomain.com  | YOUR_SERVER_IP  | 300  |

Verify propagation before proceeding:
```bash
dig +short solar.yourdomain.com
```

---

## 3. Let's Encrypt Certificate Setup

### Install certbot
```bash
sudo apt update
sudo apt install certbot -y
```

### Generate certificate (standalone mode — stop nginx first if running)
```bash
sudo certbot certonly --standalone \
  -d solar.yourdomain.com \
  --email you@yourdomain.com \
  --agree-tos \
  --non-interactive
```

Certificates are saved to:
- Certificate: `/etc/letsencrypt/live/solar.yourdomain.com/fullchain.pem`
- Private key: `/etc/letsencrypt/live/solar.yourdomain.com/privkey.pem`

### Setup auto-renewal via cron

Certificates expire after 90 days. Add a cron job to renew automatically:
```bash
sudo crontab -e
```

Add this line:
```
0 3 * * * certbot renew --quiet --pre-hook "docker compose -f /opt/solar/docker-compose.prod.yml stop nginx" --post-hook "docker compose -f /opt/solar/docker-compose.prod.yml start nginx"
```

Verify renewal works:
```bash
sudo certbot renew --dry-run
```

---

## 4. nginx Configuration

Use the provided `nginx.conf.example` as a starting point:
```bash
cp nginx.conf.example nginx.conf
sed -i 's/solar.yourdomain.com/YOUR_ACTUAL_DOMAIN/g' nginx.conf
```

Key settings in `nginx.conf.example`:
- HTTP (port 80) → HTTPS redirect
- HTTPS (port 443) with TLS 1.2/1.3 only
- Reverse proxy: `/` → frontend on port 3000, `/api/` → backend on port 8000
- Gzip compression for text assets
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)

---

## 5. docker-compose.prod.yml

The `docker-compose.prod.yml` file configures production services.

**Required environment variables — create a `.env.prod` file:**
```bash
cat > .env.prod << 'EOF'
DOMAIN=solar.yourdomain.com
ALLOWED_ORIGINS=https://solar.yourdomain.com
RATE_LIMIT_PER_MINUTE=30
EOF
```

Never commit `.env.prod` to version control. Add it to `.gitignore`.

---

## 6. Deployment Steps

### Clone and configure
```bash
git clone https://github.com/youruser/bmad-solar-panels.git /opt/solar
cd /opt/solar
cp .env.prod.example .env.prod   # create from template above
```

### Build images
```bash
docker compose -f docker-compose.prod.yml build
```

### Start services
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Verify HTTPS is working
```bash
curl -I https://solar.yourdomain.com/health
```

Expected response includes:
```
HTTP/2 200
strict-transport-security: max-age=31536000
x-frame-options: DENY
x-content-type-options: nosniff
```

### Check service health
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs backend --tail 50
```

---

## 7. Monitoring & Maintenance

### nginx access logs
```bash
docker compose -f docker-compose.prod.yml logs nginx --tail 100 -f
```

### Backend health check
```bash
curl https://solar.yourdomain.com/health
# Expected: {"status":"healthy"}
```

### Certificate expiry check
```bash
sudo certbot certificates
# or
echo | openssl s_client -connect solar.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Updating the application
```bash
cd /opt/solar
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### Stopping services
```bash
docker compose -f docker-compose.prod.yml down
```

---

## Troubleshooting

| Problem | Check |
|---------|-------|
| 502 Bad Gateway | `docker compose logs backend` — backend may be unhealthy |
| Certificate errors | Run `certbot renew --dry-run` and check cron |
| CORS errors in browser | Verify `ALLOWED_ORIGINS` matches the exact domain in `.env.prod` |
| Rate limit 429s | Reduce load or increase `RATE_LIMIT_PER_MINUTE` in `.env.prod` |
