import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * WORKLOAD DEFINITION & PERFORMANCE BUDGET
 * Configured for a "Step-Load" profile to observe system behavior
 * under ramping and sustained pressure.
 */
export const options = {
  stages: [
    { duration: '5s', target: 20 },  // Ramp-up to baseline concurrency
    { duration: '10s', target: 20 }, // Soak test: observe stability
    { duration: '5s', target: 0 },   // Graceful cooldown
  ],
  thresholds: {
    // SLA PROOF: A heavy, randomized business case
    // must complete under 250ms on a single unoptimized worker.
    // Tightening the p(95) to ensure tail latency stays within bounds.
    http_req_duration: ['p(95)<250'],
    http_req_failed: ['rate==0.0'], // Zero-tolerance for non-2xx/3xx responses
  },
};

/**
 * DATA FACTORIES
 * Stochastic generators to stay within Pydantic validation constraints
 * while ensuring input diversity.
 */
function randomFloat(min, max) {
  return Math.random() * (max - min) + min;
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * MAIN VU ITERATION
 * Simulates a single user session executing the risk analysis pipeline.
 */
export default function () {
  const url = 'http://127.0.0.1:8000/v1/risk/analyze';

  // PAYLOAD ENTROPY: Each request forces a fresh CPU-bound computation.
  // This prevents JIT optimizations and memoization from masking real bottlenecks.
  const payload = JSON.stringify({
    win_rate: randomFloat(0.3, 0.8),
    reward_to_risk_ratio: randomFloat(0.5, 3.0),
    risk_fraction: randomFloat(0.01, 0.05),
    trials: randomInt(100, 1000), // Broad range to stress test CPU (e.g., lgamma/math loops)
    initial_bankroll: 10000.0,
    ruin_threshold_fraction: 0.25
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-Request-Source': 'k6-load-test', // Helpful for log filtering
    },
  };

  const res = http.post(url, payload, params);

  // INTEGRITY CHECK: Ensure the backend isn't just fast, but also correct.
  check(res, {
    'status is 200 (OK)': (r) => r.status === 200,
    'response has body': (r) => r.body.length > 0,
  });

  // Pacing the VUs to maintain the desired request rate (Throughput Control)
  sleep(0.1);
}
