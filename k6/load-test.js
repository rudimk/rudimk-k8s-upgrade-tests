import http from 'k6/http';
import { sleep, check } from 'k6';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

export const options = {
    stages: [
        { duration: '30s', target: 200 },    // Start with 200 users
        { duration: '30s', target: 1000 },   // Ramp up to 1000 users
        { duration: '3m', target: 1000 },    // Stay at 1000 users for 3 minutes
        { duration: '30s', target: 2000 },   // Ramp up to 2000 users
        { duration: '1m', target: 2000 },    // Stay at 2000 users for 1 minute
        { duration: '30s', target: 100 },    // Ramp down to 100 users
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'],  // 95% of requests should be below 2s
        http_req_failed: ['rate<0.01'],     // Less than 1% of requests should fail
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
    // Randomly choose between data and job endpoints
    const endpoint = randomIntBetween(0, 1) === 0 ? '/data' : '/job';
    
    // Make the request
    const response = http.get(`${BASE_URL}${endpoint}`);
    
    // Check response
    check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 5000ms': (r) => r.timings.duration < 5000,
    });
    
    // Add a random sleep between 1-3 seconds to simulate user think time
    sleep(randomIntBetween(1, 3));
} 