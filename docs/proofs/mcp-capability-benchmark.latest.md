# MCP Capability Benchmark Proof

Date: 2026-03-21
Generated (UTC): 2026-03-21T07:33:55Z
Repo: /home/main/devops/atomic-kernel

Command Invoked:
npm run -s mcp:capability:benchmark

Scope:
runtime capability benchmark (HTTP + STDIO)
iterations_http: 30
iterations_stdio: 20
http_endpoint: http://127.0.0.1:18787/mcp

Transport Summary:
http ops/sec: 428.825
http p95 ms: 5.126
stdio ops/sec: 13.883
stdio p95 ms: 87.971

Threshold Failures:
(none)

Artifacts:
- artifacts/mcp-capability-benchmark.normalized.json
- artifacts/mcp-capability-benchmark.replay-hash (sha256:32efa75a19c55d527e68c8d502615dbf952814d8f9bb0077c596061439ab596e)

Result: PASS
