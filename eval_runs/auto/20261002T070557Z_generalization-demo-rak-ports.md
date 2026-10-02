# Extraction run — 2026-10-02T07:06:03+00:00

**PDF:** new_tariff_pdf/RAK-Ports-Tariff-2026.pdf
**Model:** gpt-6-luna
**Thread ID:** generalization-demo-rak-ports

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
identity: authority='Government of Ras Al Khaimah / RAK Ports' currency=None
map: 31 windows/sections, 99 sections found
assemble: 6 out-of-scope sections, general_terms_found=True
extract: first pass, all charges
port_dues: extract starting
light_dues: extract starting
towage: extract starting
light_dues: extract done
vts: extract starting
vts: extract done
pilotage: extract starting
towage: extract done
berthing_services: extract starting
pilotage: extract FAILED — OpenAIRateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for gpt-6-luna in organization org-GKE3b3XzvZ4kRzhJzdL4Zub7 on tokens per min (TPM): Limit 200000, Used 64884, Requested 136013. Please try again in 269ms. Visit https://platform.openai.com/account/rate-limits to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}
port_dues: extract done
berthing_services: extract done
validate: invalid=[]
route_after_validate: still_repairable=[] -> verify
verify: to_verify=[('light_dues', 'first'), ('port_dues', 'first'), ('towage', 'first'), ('vts', 'first'), ('berthing_services', 'first')]
