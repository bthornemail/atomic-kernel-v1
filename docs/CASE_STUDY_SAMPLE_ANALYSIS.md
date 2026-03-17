# Case Study: Sample Analysis
Status: Advisory
Authority: Projection
Depends on: `docs/APPLIED_ANALYSIS_REPORT_CONTRACT.md`

Purpose: provide a human-readable walkthrough of the deterministic sample applied analysis output.

## Source Artifact
- JSON report:
  - `runtime/atomic_kernel/fixtures/analysis-report/accept/expected-report.json`
- Markdown report:
  - `runtime/atomic_kernel/fixtures/analysis-report/accept/expected-report.md`

## Scope
Analyzed target corpus:
- `runtime/atomic_kernel/fixtures/analysis-report/accept/target-sample/`

Languages included:
- `python`
- `typescript`

## Summary (Current Fixture)
- files: `4`
- ASG nodes: `36`
- ASG edges: `32`
- patterns detected:
  - `Adapter: 1`
  - `Builder: 1`
  - `Facade: 1`
  - `Observer: 1`
  - `Strategy: 1`

## Key Findings
1. Adapter
- pattern id: `pi.adapter.PaymentAdapter`
- file: `payment.py`
- evidence includes:
  - class extension edge
  - delegated call edge to adaptee-like target

2. Builder
- pattern id: `pi.builder.ReportBuilder`
- file: `facade_builder.py`
- evidence includes:
  - staged configuration-like method
  - build method
  - construction call edge

3. Facade
- pattern id: `pi.facade.ServiceFacade`
- file: `facade_builder.py`
- evidence includes:
  - multiple subsystem call edges
  - import edge

4. Observer
- pattern id: `pi.observer.Subject`
- file: `observer_strategy.py`
- evidence includes:
  - register-like and notify-like role behavior
  - listener update-style call edge

5. Strategy
- pattern id: `pi.strategy.Context`
- file: `observer_strategy.py`
- evidence includes:
  - delegated algorithm call via `strategy.execute`

## Determinism and Trust
- Report validation is fail-closed via:
  - `scripts/validate-analysis-report.py`
- Replay lock:
  - `golden/analysis-report/replay-hash`
- Gate:
  - `scripts/analysis-report-gate.sh`

## Reproduce
```bash
cd /home/main/devops/atomic-kernel
./scripts/analysis-report-gate.sh
```

For operator output layout:
```bash
./scripts/run-applied-analysis.sh \
  --target runtime/atomic_kernel/fixtures/analysis-report/accept/target-sample \
  --name sample \
  --out-root reports/analysis
```

## Boundary
This page is a projection-level explanation of deterministic analysis outputs. It does not redefine canonical semantic contracts.

