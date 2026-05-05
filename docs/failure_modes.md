# Failure Modes

| Mode | Detection | Mitigation |
|---|---|---|
| Model hallucination | Safety agent + contradiction rules | Confidence penalty + physician flag |
| Wrong image input | Image quality gate | Reject + request rescan |
| Pediatric case | Age check | Warning modal + enhanced correlation |
| Lab-image mismatch | Contradiction rules | Downgrade ESI + flag for review |
| OOM on GPU | Monitor GPU memory | Batch size reduction, model offloading |
