# Load Testing with k6

This directory contains load testing scripts using [k6](https://k6.io/).

## Prerequisites

Install k6:

```bash
# Ubuntu/Debian
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# macOS
brew install k6

# Docker
docker pull grafana/k6
```

## Test Scripts

| Script | Description | Duration | VUs |
|--------|-------------|----------|-----|
| `smoke.js` | Basic functionality check | 1 min | 5 |
| `stress.js` | Find breaking points | 23 min | 10-100 |

## Running Tests

### Smoke Test

Quick validation that the system works under light load:

```bash
# Against local development server
k6 run tests/load/smoke.js

# Against staging
BASE_URL=https://staging-api.example.com k6 run tests/load/smoke.js

# With Docker
docker run --rm -i grafana/k6 run - <tests/load/smoke.js
```

### Stress Test

Find system limits and breaking points:

```bash
# Against local (not recommended for full stress test)
k6 run tests/load/stress.js

# Against staging
BASE_URL=https://staging-api.example.com k6 run tests/load/stress.js
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:8000` | Target API URL |

### Thresholds

#### Smoke Test
- P95 response time < 500ms
- Error rate < 1%

#### Stress Test
- P95 response time < 2000ms
- Error rate < 10%

## Results

Test results are saved to `tests/load/results/`:

```bash
# Create results directory
mkdir -p tests/load/results

# Run with results output
k6 run tests/load/smoke.js
```

### Output Formats

- **Console**: Real-time summary
- **JSON**: `*-summary.json` for programmatic analysis

## Test Scenarios

### Smoke Test (`smoke.js`)

Tests these endpoints sequentially:
1. `GET /health` - Health check
2. `POST /api/v1/calculate` - Add operation
3. `GET /api/v1/items` - List items
4. `GET /metrics` - Prometheus metrics

### Stress Test (`stress.js`)

Weighted random selection:
- 30% - Health checks
- 40% - Calculate operations
- 15% - List items
- 15% - Create items

Stages:
1. Ramp up to 10 VUs (2 min)
2. Hold at 10 VUs (5 min)
3. Ramp up to 50 VUs (2 min)
4. Hold at 50 VUs (5 min)
5. Ramp up to 100 VUs (2 min)
6. Hold at 100 VUs (5 min)
7. Ramp down to 0 VUs (2 min)

## Analyzing Results

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `http_req_duration` | Response time | P95 < threshold |
| `http_req_failed` | Failed requests | < 1% (smoke), < 10% (stress) |
| `http_reqs` | Requests per second | Higher = better |
| `errors` | Custom error rate | As low as possible |

### Response Time Analysis

```
p50 (median): Typical user experience
p90: 90% of users experience this or better
p95: Used for SLAs and thresholds
p99: Worst case (excluding outliers)
max: Absolute worst case
```

## Integration with CI/CD

Add to your GitHub Actions workflow:

```yaml
- name: Run smoke tests
  run: |
    k6 run tests/load/smoke.js
  env:
    BASE_URL: ${{ secrets.STAGING_URL }}
```

## Best Practices

1. **Never run stress tests against production**
2. **Run smoke tests after every deployment**
3. **Monitor system resources during stress tests**
4. **Compare results across test runs**
5. **Use realistic test data**

## Troubleshooting

### Connection refused
Ensure the target server is running and accessible.

### High error rates
- Check server logs
- Verify endpoint paths
- Check for rate limiting

### Slow response times
- Check server resources (CPU, memory)
- Look for database bottlenecks
- Check network latency
