# Extraction run — 2026-10-02T06:51:49+00:00

**PDF:** Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** live-full-run-with-verify

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 12 windows/sections, 123 sections found
assemble: 9 out-of-scope sections, general_terms_found=True
extract: first pass, all charges
light_dues: extract starting
port_dues: extract starting
towage: extract starting
light_dues: extract done
vts: extract starting
port_dues: extract done
pilotage: extract starting
vts: extract done
berthing_services: extract starting
towage: extract done
pilotage: extract done
berthing_services: extract done
validate: invalid=['towage']
route_after_validate: still_repairable=['towage'] -> extract
extract: verify-repairs=[] (rounds so far: {}) validate-repairs=['towage'] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 1, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
towage: extract starting
towage: extract done
validate: invalid=['towage']
route_after_validate: still_repairable=['towage'] -> extract
extract: verify-repairs=[] (rounds so far: {}) validate-repairs=['towage'] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 2, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
towage: extract starting
towage: extract done
validate: invalid=['towage']
route_after_validate: still_repairable=['towage'] -> extract
extract: verify-repairs=[] (rounds so far: {}) validate-repairs=['towage'] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 3, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
towage: extract starting
towage: extract FAILED — OpenAIConnectionError: Connection error.
validate: invalid=[]
route_after_validate: still_repairable=[] -> verify
verify: to_verify=[('light_dues', 'first'), ('port_dues', 'first'), ('vts', 'first'), ('pilotage', 'first'), ('berthing_services', 'first')]
verify: results=[('light_dues', False), ('port_dues', True), ('vts', True), ('pilotage', True), ('berthing_services', True)] verify_rounds={}
route_after_verify: still_challengeable=['port_dues', 'vts', 'pilotage', 'berthing_services'] -> extract
extract: verify-repairs=['port_dues', 'vts', 'pilotage', 'berthing_services'] (rounds so far: {}) validate-repairs=[] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 3, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
vts: extract starting
port_dues: extract starting
pilotage: extract starting
vts: extract done
berthing_services: extract starting
pilotage: extract done
port_dues: extract done
berthing_services: extract done
validate: invalid=[]
route_after_validate: still_repairable=[] -> verify
verify: to_verify=[('port_dues', 'repair'), ('vts', 'repair'), ('pilotage', 'repair'), ('berthing_services', 'repair')]
verify: results=[('port_dues', True), ('vts', False), ('pilotage', True), ('berthing_services', True)] verify_rounds={<CanonicalCharge.PORT_DUES: 'port_dues'>: 1, <CanonicalCharge.VTS: 'vts'>: 1, <CanonicalCharge.PILOTAGE: 'pilotage'>: 1, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 1}
route_after_verify: still_challengeable=[] -> finalize_statuses
```


## Final report — duration 776.0s

### Identity
```
{'authority': 'Transnet National Ports Authority', 'jurisdiction': 'South African ports of Transnet SOC (Ltd)', 'ports': ['Mossel Bay', 'East London', 'Richards Bay', 'Durban', 'Ngqura', 'Port Elizabeth', 'Cape Town', 'Saldanha Bay'], 'schedule_name': 'Port Tariffs', 'effective_from': '1 April 2024', 'effective_to': '31 March 2025', 'currency': 'ZAR'}
```
is_new_edition=True matched_existing_authority=Transnet National Ports Authority

### Coverage
- pages_read: 27/27
- general_terms_found: True
- out_of_scope_sections: 9

### Charges
#### light_dues — outcome=unmapped status=-
repair_attempts=0 verify_rounds=0
- validation history:
  - attempt 1: valid
  - attempt 2: valid
  - attempt 3: valid
  - attempt 4: valid
  - attempt 5: valid
- unmapped_source_text: 'Section 1.1.1 gives two different base calculations by vessel class: “Self-propelled vessels, vessels licensed by the Department of Environmental Affairs and Tourism, at their registered port: Per metre or part thereof of the length overall per financial year or part thereof … 24.64”; “All other vessels” are charged “Per 100 tons or part thereof … 117.08.” The first rule is based on LOA and the second on gross tonnage, so the charge as a whole cannot be represented by one of the available rule shapes, which requires a single basis.'

#### port_dues — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
  - attempt 3: valid
  - attempt 4: valid
  - attempt 5: valid
- pricing_type: 'base_plus_increment_times_duration' params: {'basic_rate': 192.73, 'daily_rate': 57.79}
- (material) The minimum of 470.98 is not a general minimum for port dues. Page 11 limits it to small vessels and pleasure vessels under Section 4.2 visiting a port other than their registered port; the proposal applies it without that limitation.
- (material) The proposed rule omits the tariff's per-100-tons-or-part-thereof unit for both the basic fee and the 24-hour increment. It instead states only gross_tonnage as the basis, which does not preserve the printed rounding/unit rule and can change the amount charged.
- (material) The proposal treats visiting vessels not engaged in trade and not mooring at a commercial berth as simply receiving a 100% reduction for the first 30 days, but omits the actual post-free-period rates: 2.82 per metre/day for the next 90 days, 5.56 for the following 90 days, 11.14 thereafter up to 12 months, and 33.45 beyond 12 months for visiting yachts and other visiting pleasure vessels. These are distinct applicability/rate terms, not covered by the proposed -100% modifier.

#### towage — outcome=? status=system_error
repair_attempts=3 verify_rounds=0
- validation history:
  - attempt 1: invalid
    - (hard) [East London] the final band's max_inclusive must be null (open-ended).
    - (hard) [Mossel Bay] the final band's max_inclusive must be null (open-ended).
  - attempt 2: invalid
    - (hard) [Richards Bay] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (hard) [Durban] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (hard) [East London] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (hard) [Port Elizabeth / Ngqura] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (hard) [Mossel Bay] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (hard) [Cape Town] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (hard) [Saldanha] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
  - attempt 3: invalid
    - (hard) [East London] the final band's max_inclusive must be null (open-ended).
    - (hard) [Mossel Bay] the final band's max_inclusive must be null (open-ended).

#### vts — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
  - attempt 3: valid
  - attempt 4: valid
  - attempt 5: valid
- per_port_rules: [('All ports excluding Durban and Saldanha Bay', 'per_unit', {'rate': 0.54}), ('Durban', 'per_unit', {'rate': 0.65}), ('Saldanha Bay', 'per_unit', {'rate': 0.65})]

#### pilotage — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
  - attempt 3: valid
  - attempt 4: valid
  - attempt 5: valid
- per_port_rules: [('Richards Bay', 'base_plus_increment', {'base': 30960.46, 'rate': 10.93}), ('Durban', 'base_plus_increment', {'base': 18608.61, 'rate': 9.72}), ('Port Elizabeth / Ngqura', 'base_plus_increment', {'base': 8970.0, 'rate': 14.33}), ('Cape Town', 'base_plus_increment', {'base': 6342.39, 'rate': 10.2}), ('Saldanha', 'base_plus_increment', {'base': 9673.57, 'rate': 13.66}), ('Other', 'base_plus_increment', {'base': 6547.45, 'rate': 10.49})]
- (material) The incremental rates are stated in the source as payable per 100 tons or part thereof, not per single gross-ton unit. The proposal gives a gross_tonnage basis without preserving the 100-ton increment, so applying the listed rate directly per GT would overcharge substantially.
- (material) The Saldanha tanker pilot-on-board-stay (PLO) duty is listed at R886.20 per hour. The proposal notes that this service incurs a per-hour charge but omits the actual rate, leaving this applicable amount unspecified.

#### berthing_services — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
  - attempt 3: valid
  - attempt 4: valid
  - attempt 5: valid
- per_port_rules: [('Richards Bay', 'base_plus_increment', {'base': 3175.89, 'rate': 13.46}), ('Port Elizabeth / Ngqura', 'base_plus_increment', {'base': 3838.62, 'rate': 18.72}), ('Cape Town', 'base_plus_increment', {'base': 3052.33, 'rate': 14.92}), ('Saldanha', 'base_plus_increment', {'base': 4006.34, 'rate': 16.97}), ('Other Ports', 'base_plus_increment', {'base': 2801.91, 'rate': 13.68})]
- (material) The increment is stated as 13.46/18.72/etc. per 100 tons or part thereof, but the proposal records only basis=gross_tonnage and rate without the 100-ton charging step. Applying the rate per gross ton rather than per 100 tons would materially overcharge; the per-100-ton unit must be retained.
- (material) The tanker-attendance hourly tariff of 1,267.83 is restricted to tanker vessels discharging crude/petroleum products at Mossel Bay and Saldanha Bay. The proposal attaches this charge to every port's rule, including Richards Bay, Cape Town, Port Elizabeth/Ngqura and Other Ports generally, so its applicability is overstated.

### Disagreements
- **port_dues**: The minimum of 470.98 is not a general minimum for port dues. Page 11 limits it to small vessels and pleasure vessels under Section 4.2 visiting a port other than their registered port; the proposal applies it without that limitation.; The proposed rule omits the tariff's per-100-tons-or-part-thereof unit for both the basic fee and the 24-hour increment. It instead states only gross_tonnage as the basis, which does not preserve the printed rounding/unit rule and can change the amount charged.; The proposal treats visiting vessels not engaged in trade and not mooring at a commercial berth as simply receiving a 100% reduction for the first 30 days, but omits the actual post-free-period rates: 2.82 per metre/day for the next 90 days, 5.56 for the following 90 days, 11.14 thereafter up to 12 months, and 33.45 beyond 12 months for visiting yachts and other visiting pleasure vessels. These are distinct applicability/rate terms, not covered by the proposed -100% modifier.
- **pilotage**: The incremental rates are stated in the source as payable per 100 tons or part thereof, not per single gross-ton unit. The proposal gives a gross_tonnage basis without preserving the 100-ton increment, so applying the listed rate directly per GT would overcharge substantially.; The Saldanha tanker pilot-on-board-stay (PLO) duty is listed at R886.20 per hour. The proposal notes that this service incurs a per-hour charge but omits the actual rate, leaving this applicable amount unspecified.
- **berthing_services**: The increment is stated as 13.46/18.72/etc. per 100 tons or part thereof, but the proposal records only basis=gross_tonnage and rate without the 100-ton charging step. Applying the rate per gross ton rather than per 100 tons would materially overcharge; the per-100-ton unit must be retained.; The tanker-attendance hourly tariff of 1,267.83 is restricted to tanker vessels discharging crude/petroleum products at Mossel Bay and Saldanha Bay. The proposal attaches this charge to every port's rule, including Richards Bay, Cape Town, Port Elizabeth/Ngqura and Other Ports generally, so its applicability is overstated.
