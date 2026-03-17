# Applied Analysis Report

- v: `analysis-report.v0`
- authority: `advisory`
- target: `/home/main/devops/atomic-kernel/runtime/atomic_kernel/fixtures/analysis-report/accept/target-sample`
- languages: `python, typescript`

## Summary
- files: 4
- asg_nodes: 36
- asg_edges: 32
- domain counts:
  - core: 4
- pattern counts:
  - Adapter: 1
  - Builder: 1
  - Facade: 1
  - Observer: 1
  - Strategy: 1

## Instances
- Adapter `pi.adapter.PaymentAdapter` in `payment.py` confidence=0.91
- Builder `pi.builder.ReportBuilder` in `facade_builder.py` confidence=0.8
- Facade `pi.facade.ServiceFacade` in `facade_builder.py` confidence=0.83
- Observer `pi.observer.Subject` in `observer_strategy.py` confidence=0.84
- Strategy `pi.strategy.Context` in `observer_strategy.py` confidence=0.82

## Digests
- inputs_digest: `sha256:0a0d02d9cdf4e23e5ca277abca1ae9ca2d19609b41ecae48f751d8d82a6e991b`
- evidence_digest: `sha256:f39f825649a3aa8f5f6a4b1cf667d09204acd37aa81a3f1257c4f54cbea811b2`
- outputs_digest: `sha256:6eea65df632330d6357e6534a3257ac004bb7b1f06bf6cf77dda47b651697d33`
