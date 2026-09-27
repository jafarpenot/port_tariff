# Extraction run — 2026-09-27T18:15:32+00:00

**PDF:** Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** graph-live-verify

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 9 windows, 141 sections found
assemble: 37 out-of-scope sections, general_terms_found=True
extract: first pass, all charges
validate: invalid=['towage']
route_after_validate: still_repairable=['towage'] -> extract
extract: verify-repairs=[] (rounds so far: {}) validate-repairs=['towage'] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 1, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
validate: invalid=[]
route_after_validate: still_repairable=[] -> verify
verify: to_verify=[('light_dues', 'first'), ('port_dues', 'first'), ('towage', 'first'), ('vts', 'first'), ('pilotage', 'first'), ('berthing_services', 'first')]
verify: results=[('light_dues', True), ('port_dues', True), ('towage', True), ('vts', False), ('pilotage', True), ('berthing_services', True)] verify_rounds={}
route_after_verify: still_challengeable=['light_dues', 'port_dues', 'towage', 'pilotage', 'berthing_services'] -> extract
extract: verify-repairs=['light_dues', 'port_dues', 'towage', 'pilotage', 'berthing_services'] (rounds so far: {}) validate-repairs=[] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 1, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
