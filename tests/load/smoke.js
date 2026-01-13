import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const healthCheckDuration = new Trend('health_check_duration');
const calculateDuration = new Trend('calculate_duration');

// Configuration for smoke test
// Light load to verify basic functionality
export const options = {
    vus: 5,              // 5 virtual users
    duration: '1m',      // Run for 1 minute
    thresholds: {
        http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
        errors: ['rate<0.01'],              // Error rate under 1%
        http_req_failed: ['rate<0.01'],     // HTTP failures under 1%
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
    // Test 1: Health check endpoint
    const healthRes = http.get(`${BASE_URL}/health`);
    healthCheckDuration.add(healthRes.timings.duration);

    check(healthRes, {
        'health: status is 200': (r) => r.status === 200,
        'health: response has status field': (r) => {
            const body = JSON.parse(r.body);
            return body.status === 'healthy';
        },
    }) || errorRate.add(1);

    sleep(0.5);

    // Test 2: Calculate endpoint (add operation)
    const addPayload = JSON.stringify({
        a: Math.floor(Math.random() * 100),
        b: Math.floor(Math.random() * 100),
        operation: 'add',
    });

    const addRes = http.post(`${BASE_URL}/api/v1/calculate`, addPayload, {
        headers: { 'Content-Type': 'application/json' },
    });
    calculateDuration.add(addRes.timings.duration);

    check(addRes, {
        'calculate add: status is 200': (r) => r.status === 200,
        'calculate add: result is correct': (r) => {
            const body = JSON.parse(r.body);
            return body.result !== undefined;
        },
    }) || errorRate.add(1);

    sleep(0.5);

    // Test 3: Items endpoint (GET)
    const itemsRes = http.get(`${BASE_URL}/api/v1/items`);

    check(itemsRes, {
        'items: status is 200': (r) => r.status === 200,
        'items: response is array': (r) => {
            const body = JSON.parse(r.body);
            return Array.isArray(body);
        },
    }) || errorRate.add(1);

    sleep(0.5);

    // Test 4: Metrics endpoint
    const metricsRes = http.get(`${BASE_URL}/metrics`);

    check(metricsRes, {
        'metrics: status is 200': (r) => r.status === 200,
        'metrics: contains prometheus format': (r) => {
            return r.body.includes('http_requests_total') ||
                   r.body.includes('process_');
        },
    }) || errorRate.add(1);

    sleep(1);
}

export function handleSummary(data) {
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'tests/load/results/smoke-summary.json': JSON.stringify(data),
    };
}

function textSummary(data, options) {
    const { metrics, root_group } = data;
    let summary = '\n=== SMOKE TEST SUMMARY ===\n\n';

    summary += `Total Requests: ${metrics.http_reqs.values.count}\n`;
    summary += `Failed Requests: ${metrics.http_req_failed.values.passes}\n`;
    summary += `Average Response Time: ${metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
    summary += `P95 Response Time: ${metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
    summary += `Error Rate: ${(metrics.errors?.values?.rate * 100 || 0).toFixed(2)}%\n`;

    return summary;
}
