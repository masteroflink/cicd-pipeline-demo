import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const requestDuration = new Trend('request_duration');
const successfulRequests = new Counter('successful_requests');
const failedRequests = new Counter('failed_requests');

// Stress test configuration
// Ramp up load to find breaking points
export const options = {
    stages: [
        { duration: '2m', target: 10 },   // Ramp up to 10 users
        { duration: '5m', target: 10 },   // Stay at 10 users
        { duration: '2m', target: 50 },   // Ramp up to 50 users
        { duration: '5m', target: 50 },   // Stay at 50 users
        { duration: '2m', target: 100 },  // Ramp up to 100 users
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 0 },    // Ramp down to 0 users
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
        errors: ['rate<0.1'],               // Error rate under 10%
        http_req_failed: ['rate<0.1'],      // HTTP failures under 10%
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Operations to test
const operations = ['add', 'subtract', 'multiply', 'divide'];

export default function () {
    // Weighted random endpoint selection
    const rand = Math.random();

    if (rand < 0.3) {
        // 30% - Health check (lightweight)
        testHealthCheck();
    } else if (rand < 0.7) {
        // 40% - Calculate (main workload)
        testCalculate();
    } else if (rand < 0.85) {
        // 15% - Items list
        testItemsList();
    } else {
        // 15% - Create item
        testCreateItem();
    }

    // Small random delay between requests
    sleep(Math.random() * 0.5);
}

function testHealthCheck() {
    const res = http.get(`${BASE_URL}/health`);
    requestDuration.add(res.timings.duration);

    const success = check(res, {
        'health: status is 200': (r) => r.status === 200,
    });

    if (success) {
        successfulRequests.add(1);
    } else {
        failedRequests.add(1);
        errorRate.add(1);
    }
}

function testCalculate() {
    const operation = operations[Math.floor(Math.random() * operations.length)];
    let a = Math.floor(Math.random() * 100) + 1;
    let b = Math.floor(Math.random() * 100) + 1;

    // Avoid division by zero
    if (operation === 'divide' && b === 0) {
        b = 1;
    }

    const payload = JSON.stringify({ a, b, operation });

    const res = http.post(`${BASE_URL}/api/v1/calculate`, payload, {
        headers: { 'Content-Type': 'application/json' },
    });
    requestDuration.add(res.timings.duration);

    const success = check(res, {
        'calculate: status is 200': (r) => r.status === 200,
        'calculate: has result': (r) => {
            try {
                const body = JSON.parse(r.body);
                return body.result !== undefined;
            } catch {
                return false;
            }
        },
    });

    if (success) {
        successfulRequests.add(1);
    } else {
        failedRequests.add(1);
        errorRate.add(1);
    }
}

function testItemsList() {
    const res = http.get(`${BASE_URL}/api/v1/items`);
    requestDuration.add(res.timings.duration);

    const success = check(res, {
        'items: status is 200': (r) => r.status === 200,
    });

    if (success) {
        successfulRequests.add(1);
    } else {
        failedRequests.add(1);
        errorRate.add(1);
    }
}

function testCreateItem() {
    const payload = JSON.stringify({
        name: `Item ${Date.now()}`,
        description: `Stress test item created at ${new Date().toISOString()}`,
    });

    const res = http.post(`${BASE_URL}/api/v1/items`, payload, {
        headers: { 'Content-Type': 'application/json' },
    });
    requestDuration.add(res.timings.duration);

    const success = check(res, {
        'create item: status is 201': (r) => r.status === 201,
    });

    if (success) {
        successfulRequests.add(1);
    } else {
        failedRequests.add(1);
        errorRate.add(1);
    }
}

export function handleSummary(data) {
    return {
        'stdout': textSummary(data),
        'tests/load/results/stress-summary.json': JSON.stringify(data),
    };
}

function textSummary(data) {
    const { metrics } = data;
    let summary = '\n=== STRESS TEST SUMMARY ===\n\n';

    summary += `Total Requests: ${metrics.http_reqs.values.count}\n`;
    summary += `Successful Requests: ${metrics.successful_requests?.values?.count || 0}\n`;
    summary += `Failed Requests: ${metrics.failed_requests?.values?.count || 0}\n`;
    summary += `\nResponse Times:\n`;
    summary += `  Average: ${metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
    summary += `  Median: ${metrics.http_req_duration.values.med.toFixed(2)}ms\n`;
    summary += `  P90: ${metrics.http_req_duration.values['p(90)'].toFixed(2)}ms\n`;
    summary += `  P95: ${metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
    summary += `  Max: ${metrics.http_req_duration.values.max.toFixed(2)}ms\n`;
    summary += `\nThroughput: ${(metrics.http_reqs.values.rate).toFixed(2)} req/s\n`;
    summary += `Error Rate: ${(metrics.errors?.values?.rate * 100 || 0).toFixed(2)}%\n`;

    return summary;
}
