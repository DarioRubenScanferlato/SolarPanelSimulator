# Security Checklist

Use this checklist before every production launch and after significant configuration changes.

---

## Pre-Deployment

### Environment Variables
- [ ] `ENV=production` is set in the backend container (not `development`)
- [ ] `ALLOWED_ORIGINS` is set to the exact production domain (e.g. `https://solar.yourdomain.com`) — no wildcards
- [ ] `RATE_LIMIT_PER_MINUTE` is set (recommended: 30 for production)
- [ ] No `.env.prod` or secrets file committed to the repository
- [ ] `.env.prod` is listed in `.gitignore`

### HTTPS / TLS
- [ ] Let's Encrypt certificate is valid (`certbot certificates` shows "VALID")
- [ ] Certificate auto-renewal cron job is active (`sudo crontab -l`)
- [ ] HTTP (port 80) redirects to HTTPS — verify with `curl -I http://solar.yourdomain.com`
- [ ] TLS 1.0 and 1.1 are disabled in nginx (only 1.2 and 1.3 allowed)

### CORS
- [ ] `ALLOWED_ORIGINS` contains only the production domain — no `localhost`, no wildcards
- [ ] OPTIONS preflight returns correct `Access-Control-Allow-Origin` header
- [ ] Requests from unexpected origins are rejected (test with curl from different origin)

### Rate Limiting
- [ ] `/simulate` endpoint returns HTTP 429 after the configured limit (test: send >30 requests/minute)
- [ ] Rate limit is IP-based (not user-based — no auth implemented)

### Error Masking
- [ ] Backend returns generic `"Simulation failed. Please try again."` for internal errors — not stack traces
- [ ] Verify: trigger a 500 error and check the response body contains no file paths or tracebacks
- [ ] Server-side logs capture the full traceback for ops debugging

### Security Headers
Run this command and verify all headers are present:
```bash
curl -sI https://solar.yourdomain.com | grep -E "x-content|x-frame|x-xss|strict-transport"
```

Expected output:
```
x-content-type-options: nosniff
x-frame-options: DENY
x-xss-protection: 1; mode=block
strict-transport-security: max-age=31536000
```

- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY`
- [ ] `X-XSS-Protection: 1; mode=block`
- [ ] `Strict-Transport-Security: max-age=31536000`

---

## Post-Deployment Validation

### Functional checks
- [ ] Frontend loads at `https://solar.yourdomain.com`
- [ ] Simulation returns results (run one simulation end-to-end)
- [ ] `/health` returns `{"status":"healthy"}`

### Security header scan
```bash
# Full header dump
curl -sI https://solar.yourdomain.com
curl -sI https://solar.yourdomain.com/health
```

### HTTPS redirect verification
```bash
curl -sI http://solar.yourdomain.com | head -5
# Should show: HTTP/1.1 301 Moved Permanently
# Location: https://solar.yourdomain.com/
```

### Rate limit test
```bash
# Send 35 requests — the last few should return 429
for i in $(seq 1 35); do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    https://solar.yourdomain.com/api/simulate \
    -H "Content-Type: application/json" \
    -d '{"latitude":45,"longitude":7,"panel_count":1,"panel_area_m2":2,"panel_efficiency":20,"tilt_angle_deg":35,"azimuth_deg":180,"start_date":"2026-06-21","duration_days":1}')
  echo "Request $i: $code"
done
```

---

## Runtime Security

### Regular log review
- [ ] Review nginx access logs weekly for unusual patterns (high request rates, scanning)
- [ ] Review backend error logs for recurring 500 errors
- [ ] Monitor for 429 rate limit hits that may indicate abuse

### Certificate monitoring
- [ ] Check certificate expiry monthly: `certbot certificates`
- [ ] Verify cron auto-renewal ran successfully (check `/var/log/syslog` for certbot entries)

### Dependency updates
- [ ] Review Python dependencies quarterly (`uv lock --upgrade` in a test environment first)
- [ ] Apply security patches for base Docker images (rebuild on `python:3.11-slim` updates)

---

## Known Limitations

- Rate limiting is IP-based with in-memory storage — resets on backend restart and does not persist across multiple instances
- No authentication — the `/simulate` endpoint is public
- Weather model is heuristic (not real-time) — no external API keys required or exposed
