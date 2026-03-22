import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5s', target: 20 },
    { duration: '10s', target: 20 },
    { duration: '5s', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<250'], // Business SLA for typical analytical queries
    'http_req_failed': ['rate==0.0'],
  },
};

export default function () {
  const url = 'http://127.0.0.1:8000/v1/risk/analyze';

  // Payload represents a typical quarterly trader activity (~300 trades)
  const payload = JSON.stringify({
    win_rate: 0.55,
    reward_to_risk_ratio: 1.2,
    risk_fraction: 0.02,
    trials: 300,
    initial_bankroll: 10000,
    ruin_threshold_fraction: 0.25
  });

  const res = http.post(url, payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(res, {
    'is status 200': (r) => r.status === 200,
    'has metrics': (r) => r.json('metrics.expected_log_growth_per_trial') !== undefined,
  });

  sleep(0.1); // Pacing to stabilize throughput per VU
}
