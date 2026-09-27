# Extraction run — 2026-09-27T11:49:29+00:00

**PDF:** Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** full-tnpa-after-structure-scan

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
structure_scan: 4093 chars
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 7 windows, 137 sections found
assemble: 13 out-of-scope sections, general_terms_found=True
light_dues: starting, context pages=[5, 6, 7, 8, 9, 17] sections=['SECTION 6', '1', '1.1', '1.1.1']
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: validate -> valid
light_dues: verify -> clean
light_dues: done
port_dues: starting, context pages=[5, 13, 14, 15, 16, 17] sections=['SECTION 6', '4', '4.1', '4.1.1', '4.2', '4.1.2']
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: done
towage: starting, context pages=[5, 9, 13, 17] sections=['SECTION 6', '3', '3.1', '3.2', '3.6', '3.7', '3.7 (continuation; number not shown on these pages)', '3.9', '4.8', '4', '4.1']
towage: validate -> valid
towage: verify -> material finding
towage: validate -> valid
towage: verify -> material finding
towage: done
vts: starting, context pages=[5, 9, 13, 14, 15, 16, 17] sections=['SECTION 6', '2', '2.1', '2.1.1', '4.2', '4']
vts: validate -> valid
vts: verify -> clean
vts: done
pilotage: starting, context pages=[5, 9, 17] sections=['SECTION 6', '3', '3.1', '3.2', '3.3', '3.5']
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: repair round left outcome as 'not_present' instead of mapped -- rejected
pilotage: validate -> invalid
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: done
berthing_services: starting, context pages=[5, 9, 10, 11, 12, 13, 17] sections=['SECTION 6', '3', '3.1', '3.2', '3.8', '3.9']
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: done
```


## Final report — duration 1253.3s

### Identity
```
{'authority': 'Transnet National Ports Authority', 'jurisdiction': 'South African ports', 'ports': [], 'schedule_name': 'Port Tariffs', 'effective_from': '1 April 2024', 'effective_to': '31 March 2025', 'currency': 'ZAR'}
```
is_new_edition=True matched_existing_authority=Transnet National Ports Authority

### Coverage
- pages_read: 27/27
- general_terms_found: True
- out_of_scope_sections: 13

### Charges
#### light_dues — outcome=unmapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
- unmapped_source_text: '“Per metre or part thereof of the length overall per financial year or part thereof … 24.64” for specified self-propelled/licensed vessels; “Per 100 tons or part thereof … 117.08” for all other vessels. The base calculation differs by vessel class (LOA versus tonnage, with different billing periods), and cannot be represented as one of the fixed pricing shapes for a single rule.'

#### port_dues — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
- pricing_type: 'per_unit' params: {'rate': 2.82}
- (material) The proposal maps the charge as a flat per-call rate of 2.82 with no rate tiers. The source says the free 30-day period is followed by escalating daily rates: 2.82 for the next 90 days, 5.56 for the following 90 days, 11.14 thereafter up to 12 months, and 33.45 for visits exceeding 12 months. The later rates and their time conditions are omitted from the mapped rule.

#### towage — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha] value 16095.12 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth] value 22050.3 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [At the Port of Saldanha for services of a special nature] value 20301.18 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 16095.12 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Large Tug] value 22050.3 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Large Tug] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Large Tug] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Large Tug] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Large Tug] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Saldanha — Large Tug, services of a special nature] value 20301.18 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Saldanha — Large Tug, services of a special nature] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Saldanha — Large Tug, services of a special nature] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Saldanha — Large Tug, services of a special nature] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Saldanha — Large Tug, services of a special nature] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 5955.53 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of East London — Small Tug/ Workboat] value 9851.06 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of East London — Small Tug/ Workboat] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of East London — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of East London — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of East London — Small Tug/ Workboat] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 8159.07 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- per_port_rules: [('All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug', 'per_unit', {'rate': 16095.12}), ('Port of Ngqura/Port Elizabeth — Large Tug', 'per_unit', {'rate': 22050.3}), ('Port of Saldanha — Large Tug, services of a special nature', 'per_unit', {'rate': 20301.18}), ('All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat', 'per_unit', {'rate': 5955.53}), ('Port of East London — Small Tug/ Workboat', 'per_unit', {'rate': 9851.06}), ('Port of Ngqura/Port Elizabeth — Small Tug/ Workboat', 'per_unit', {'rate': 8159.07})]
- warning: [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 16095.12 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of Ngqura, Port Elizabeth and Saldanha — Large Tug] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Large Tug] value 22050.3 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Large Tug] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Large Tug] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Large Tug] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Large Tug] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Saldanha — Large Tug, services of a special nature] value 20301.18 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Saldanha — Large Tug, services of a special nature] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Saldanha — Large Tug, services of a special nature] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Saldanha — Large Tug, services of a special nature] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Saldanha — Large Tug, services of a special nature] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 5955.53 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [All Ports, except the Port of East London, Ngqura and Port Elizabeth — Small Tug/ Workboat] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of East London — Small Tug/ Workboat] value 9851.06 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of East London — Small Tug/ Workboat] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of East London — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of East London — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of East London — Small Tug/ Workboat] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 8159.07 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port of Ngqura/Port Elizabeth — Small Tug/ Workboat] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal omits the separate 3.6 towage tariff charged per service based on vessel tonnage. The source gives port-specific base rates for tonnage bands (up to 2,000; 2,001–10,000; 10,000–50,000; 50,001–100,000; and above 100,000), plus incremental per-100-ton charges and stated maxima. Recording only the later hourly "Other vessel services" tug rates leaves out these charge amounts.
- (material) The proposal omits the 3.6 surcharge rule for a tug/vessel requested to remain or come on duty outside ordinary working hours when that request is cancelled after standby has commenced: the source says the fee is payable as if the service had been performed, with normal fees enhanced by 25%. This can change the amount charged.

#### vts — outcome=mapped status=-
repair_attempts=0 verify_rounds=0
- per_port_rules: [('All ports excluding Durban and Saldanha Bay', 'per_unit', {'rate': 0.54}), ('Durban', 'per_unit', {'rate': 0.65}), ('Saldanha Bay', 'per_unit', {'rate': 0.65})]
- warning: [All ports excluding Durban and Saldanha Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.

#### pilotage — outcome=mapped status=-
repair_attempts=1 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) [Richards Bay] value 30960.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 10.93 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 18608.61 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 9.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 8970.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 14.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 6342.39 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 10.2 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 9673.57 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 13.66 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 10.49 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: invalid
    - (hard) This charge was already committed as mapped, but this repair round's outcome is 'not_present' instead. A repair may only fix the structure/content of a proposal already mapped, never change outcome away from it. Restore outcome to 'mapped' and address the original concern within the proposal itself.
  - attempt 3: valid
    - (warning) [Richards Bay] value 30960.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 10.93 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 18608.61 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 9.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 8970.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 14.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 6342.39 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 10.2 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 9673.57 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 13.66 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 10.49 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- per_port_rules: [('Richards Bay', 'base_plus_increment', {'base': 30960.46, 'rate': 10.93}), ('Durban', 'base_plus_increment', {'base': 18608.61, 'rate': 9.72}), ('Port Elizabeth / Ngqura', 'base_plus_increment', {'base': 8970.0, 'rate': 14.33}), ('Cape Town', 'base_plus_increment', {'base': 6342.39, 'rate': 10.2}), ('Saldanha', 'base_plus_increment', {'base': 9673.57, 'rate': 13.66}), ('Other', 'base_plus_increment', {'base': 6547.45, 'rate': 10.49})]
- warning: [Richards Bay] value 30960.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 10.93 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 18608.61 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 9.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 8970.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 14.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 6342.39 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 10.2 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 9673.57 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 13.66 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 10.49 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The tariff states that the variable charge is per 100 tons or part thereof, but the proposal records only basis=gross_tonnage and a rate, with no 100-ton unit/rounding step. Applying the rate per ton rather than per 100 tons (or part) would materially change the charge.
- (material) The proposal omits the rule that any vessel movement without the Authority’s consent is charged full pilotage charges as if the service had been performed. This affects when the full charge applies.

#### berthing_services — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) [Richards Bay] value 3175.89 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 13.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 3838.62 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 18.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 3052.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 14.92 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 4006.34 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 16.97 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 2801.91 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 13.68 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) [Richards Bay] value 3175.89 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 13.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 3838.62 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 18.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 3052.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 14.92 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 4006.34 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 16.97 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 2801.91 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 13.68 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- per_port_rules: [('Richards Bay', 'base_plus_increment', {'base': 3175.89, 'rate': 13.46}), ('Port Elizabeth / Ngqura', 'base_plus_increment', {'base': 3838.62, 'rate': 18.72}), ('Cape Town', 'base_plus_increment', {'base': 3052.33, 'rate': 14.92}), ('Saldanha', 'base_plus_increment', {'base': 4006.34, 'rate': 16.97}), ('Other Ports', 'base_plus_increment', {'base': 2801.91, 'rate': 13.68})]
- warning: [Richards Bay] value 3175.89 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 13.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 3838.62 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 18.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 3052.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 14.92 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 4006.34 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 16.97 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other Ports] value 2801.91 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other Ports] value 13.68 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The tariff states that the tonnage increment is charged “per 100 tons or part thereof,” but the proposal records only basis=gross_tonnage and rate=13.46 (and corresponding rates for other ports), without preserving the 100-ton unit. This can produce a materially different charge if the rates are applied per gross ton rather than per 100 tons.

### Disagreements
- **port_dues**: The proposal maps the charge as a flat per-call rate of 2.82 with no rate tiers. The source says the free 30-day period is followed by escalating daily rates: 2.82 for the next 90 days, 5.56 for the following 90 days, 11.14 thereafter up to 12 months, and 33.45 for visits exceeding 12 months. The later rates and their time conditions are omitted from the mapped rule.
- **towage**: The proposal omits the separate 3.6 towage tariff charged per service based on vessel tonnage. The source gives port-specific base rates for tonnage bands (up to 2,000; 2,001–10,000; 10,000–50,000; 50,001–100,000; and above 100,000), plus incremental per-100-ton charges and stated maxima. Recording only the later hourly "Other vessel services" tug rates leaves out these charge amounts.; The proposal omits the 3.6 surcharge rule for a tug/vessel requested to remain or come on duty outside ordinary working hours when that request is cancelled after standby has commenced: the source says the fee is payable as if the service had been performed, with normal fees enhanced by 25%. This can change the amount charged.
- **pilotage**: The tariff states that the variable charge is per 100 tons or part thereof, but the proposal records only basis=gross_tonnage and a rate, with no 100-ton unit/rounding step. Applying the rate per ton rather than per 100 tons (or part) would materially change the charge.; The proposal omits the rule that any vessel movement without the Authority’s consent is charged full pilotage charges as if the service had been performed. This affects when the full charge applies.
- **berthing_services**: The tariff states that the tonnage increment is charged “per 100 tons or part thereof,” but the proposal records only basis=gross_tonnage and rate=13.46 (and corresponding rates for other ports), without preserving the 100-ton unit. This can produce a materially different charge if the rates are applied per gross ton rather than per 100 tons.
