import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5s', target: 20 },
    { duration: '10s', target: 20 },
    { duration: '5s', target: 0 },
  ],
  thresholds: {
    // SLA PROOF: A heavy business case (e.g., 1000 trades)
    // must complete under 250ms on a single unoptimized worker.
    http_req_duration: ['p(95)<250'],
    http_req_failed: ['rate==0.0'],
  },
};

export default function () {
  const url = 'http://127.0.0.1:8000/v1/risk/analyze';

  // Solid, heavy business case (e.g., ~3 years of active trading history)
  const payload = JSON.stringify({
    win_rate: 0.55,
    reward_to_risk_ratio: 1.2,
    risk_fraction: 0.02,
    trials: 1000,
    initial_bankroll: 10000,
    ruin_threshold_fraction: 0.25
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(url, payload, params);

  check(res, {
    'is status 200': (r) => r.status === 200,
  });

  sleep(0.1);
}
