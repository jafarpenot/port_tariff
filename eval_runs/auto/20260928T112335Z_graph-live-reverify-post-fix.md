# Extraction run — 2026-09-28T11:23:35+00:00

**PDF:** /Users/jafarpenot/Desktop/my_projs/port_tariff/Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** graph-live-reverify-post-fix

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 9 windows, 213 sections found
assemble: 38 out-of-scope sections, general_terms_found=True
extract: first pass, all charges
light_dues: extract starting
port_dues: extract starting
towage: extract starting
light_dues: extract done
vts: extract starting
port_dues: extract done
pilotage: extract starting
towage: extract done
berthing_services: extract starting
vts: extract done
pilotage: extract done
berthing_services: extract done
validate: invalid=['towage']
route_after_validate: still_repairable=['towage'] -> extract
extract: verify-repairs=[] (rounds so far: {}) validate-repairs=['towage'] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 1, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
towage: extract starting
towage: extract done
validate: invalid=[]
route_after_validate: still_repairable=[] -> verify
verify: to_verify=[('light_dues', 'first'), ('port_dues', 'first'), ('towage', 'first'), ('vts', 'first'), ('pilotage', 'first'), ('berthing_services', 'first')]
verify: results=[('light_dues', True), ('port_dues', True), ('towage', True), ('vts', True), ('pilotage', True), ('berthing_services', True)] verify_rounds={}
route_after_verify: still_challengeable=['light_dues', 'port_dues', 'towage', 'vts', 'pilotage', 'berthing_services'] -> extract
extract: verify-repairs=['light_dues', 'port_dues', 'towage', 'vts', 'pilotage', 'berthing_services'] (rounds so far: {}) validate-repairs=[] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 1, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
light_dues: extract starting
port_dues: extract starting
towage: extract starting
light_dues: extract done
vts: extract starting
towage: extract done
pilotage: extract starting
port_dues: extract done
berthing_services: extract starting
vts: extract done
berthing_services: extract done
pilotage: extract done
validate: invalid=['towage']
route_after_validate: still_repairable=['towage'] -> extract
extract: verify-repairs=[] (rounds so far: {}) validate-repairs=['towage'] (repair_counts: {<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 0, <CanonicalCharge.PORT_DUES: 'port_dues'>: 0, <CanonicalCharge.TOWAGE: 'towage'>: 2, <CanonicalCharge.VTS: 'vts'>: 0, <CanonicalCharge.PILOTAGE: 'pilotage'>: 0, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 0})
towage: extract starting
towage: extract done
validate: invalid=[]
route_after_validate: still_repairable=[] -> verify
verify: to_verify=[('light_dues', 'repair'), ('port_dues', 'repair'), ('towage', 'repair'), ('vts', 'repair'), ('pilotage', 'repair'), ('berthing_services', 'repair')]
verify: results=[('light_dues', True), ('port_dues', True), ('towage', True), ('vts', True), ('pilotage', True), ('berthing_services', False)] verify_rounds={<CanonicalCharge.LIGHT_DUES: 'light_dues'>: 1, <CanonicalCharge.PORT_DUES: 'port_dues'>: 1, <CanonicalCharge.TOWAGE: 'towage'>: 1, <CanonicalCharge.VTS: 'vts'>: 1, <CanonicalCharge.PILOTAGE: 'pilotage'>: 1, <CanonicalCharge.BERTHING_SERVICES: 'berthing_services'>: 1}
route_after_verify: still_challengeable=[] -> finalize_statuses
```


## Final report — duration 732.9s

### Identity
```
{'authority': 'Transnet National Ports Authority', 'jurisdiction': 'South African ports of Transnet SOC (Ltd)', 'ports': ['Richards Bay', 'Durban', 'Port Elizabeth', 'Ngqura', 'Cape Town', 'Saldanha', 'East London', 'Mossel Bay'], 'schedule_name': 'Port Tariffs', 'effective_from': '1 April 2024', 'effective_to': '31 March 2025', 'currency': 'ZAR'}
```
is_new_edition=True matched_existing_authority=Transnet National Ports Authority

### Coverage
- pages_read: 27/27
- general_terms_found: True
- out_of_scope_sections: 38

### Charges
#### light_dues — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
  - attempt 3: valid
    - (warning) value 117.08 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 4: valid
    - (warning) value 117.08 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- pricing_type: 'per_unit' params: {'rate': 117.08}
- warning: value 117.08 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal applies the R117.08-per-100-tons tariff to all vessels as though it were a per-call charge. The source lists a separate rate for self-propelled vessels and vessels licensed by the Department of Environmental Affairs and Tourism at their registered port: R24.64 per metre or part thereof of length overall per financial year or part thereof. This rate and its applicability are missing from the proposal.
- (material) The proposal omits the explicit condition that vessels remaining within a specific port for extended periods are charged only once and are not affected by length of stay. This may affect the charge for such vessels.
- (minor) The proposal describes the exemption categories as receiving a 100% reduction, but omits the exemption for foreign naval/war vessels, which the source lists separately under Exemptions.

#### port_dues — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) value 192.73 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 57.79 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -35.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 20.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -60.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -10.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -15.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) value 192.73 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 57.79 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -35.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 20.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -60.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -10.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -15.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: valid
    - (warning) value 192.73 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 57.79 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -35.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 20.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -60.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -10.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -15.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 4: valid
    - (warning) value 192.73 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 57.79 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -35.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 20.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -60.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -10.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -15.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- pricing_type: 'base_plus_increment_times_duration' params: {'basic_rate': 192.73, 'daily_rate': 57.79}
- warning: value 192.73 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value 57.79 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -35.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value 20.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -60.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -10.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -15.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal omits the explicit applicability condition that these port dues are payable by vessels entering the port from passing the entrance inward until passing it outward, and also by vessels taking in bunkers at the designated anchorage and vessels at offshore moorings or similar facilities. This is part of the charge's charging scope, not just its label.
- (material) The proposal misstates the surcharge trigger as vessels that are not engaged in cargo working OR undergoing repairs. The source says vessels in port longer than 30 days that are not engaged in cargo working OR undergoing repairs will be liable; this means the exclusion applies when the vessel is undergoing repairs, and the surcharge is for those neither cargo-working nor undergoing repairs.
- (material) The proposal leaves the surcharge base as the 'incremental port-dues fee,' but the source says a 20% surcharge on the incremental fee of port dues; its interaction with the 35% reduction is not stated as the proposal's wording may imply. This needs to preserve the source's stated base rather than imply that the incremental amount is necessarily the post-reduction fee.
- (minor) The proposal describes the vessel-in-port-under-12-hours reduction as applying to 'a vessel remaining in port for less than 12 hours'; the source calls it a reduction of 15% and explicitly says it is in addition to other reductions that may be enjoyed. That stacking condition is omitted from this modifier.
- (minor) The proposal's 35% reduction modifier omits that the small-vessel category is specifically Section 4, Clause 4.2 vessels visiting a port other than their registered port; while this condition appears in a separate minimum-fee modifier, it should be stated as part of the reduction's eligibility condition too.
- (minor) The proposal omits the required submission of proof to the Authority before the vessel sails to obtain the 10% reduction for qualifying tanker certifications.

#### towage — outcome=mapped status=-
repair_attempts=2 verify_rounds=1
- validation history:
  - attempt 1: invalid
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [East London] the final band's max_inclusive must be null (open-ended).
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Mossel Bay] the final band's max_inclusive must be null (open-ended).
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: invalid
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [East London] the final band's max_inclusive must be null (open-ended).
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Mossel Bay] the final band's max_inclusive must be null (open-ended).
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 10152.19 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 4: valid
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- per_port_rules: [('Richards Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7001.67, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 13020.67, 'increment_above': 2000.0, 'per_unit_rate': 275.32}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 39999.88, 'increment_above': 10000.0, 'per_unit_rate': 101.08}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 79999.76, 'increment_above': 50000.0, 'per_unit_rate': 30.11}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 103999.7, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Durban', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 8140.0, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 12633.99, 'increment_above': 2000.0, 'per_unit_rate': 268.99}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 38494.51, 'increment_above': 10000.0, 'per_unit_rate': 84.95}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 73118.07, 'increment_above': 50000.0, 'per_unit_rate': 32.24}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 93548.13, 'increment_above': 100000.0, 'per_unit_rate': 23.65}]}), ('East London', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5622.16, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 200.97}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27956.91, 'increment_above': 10000.0, 'per_unit_rate': 66.67}, {'min_exclusive': 50000.0, 'max_inclusive': None, 'base': 55913.82, 'increment_above': 50000.0, 'per_unit_rate': 25.8}]}), ('Port Elizabeth / Ngqura', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7206.98, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 11168.45, 'increment_above': 2000.0, 'per_unit_rate': 237.53}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 32257.98, 'increment_above': 10000.0, 'per_unit_rate': 73.1}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 64515.95, 'increment_above': 50000.0, 'per_unit_rate': 21.5}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 82542.46, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Mossel Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 6316.53, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 173.37}, {'min_exclusive': 10000.0, 'max_inclusive': None, 'base': 25806.37, 'increment_above': 10000.0, 'per_unit_rate': 60.21}]}), ('Cape Town', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5411.47, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 7898.57, 'increment_above': 2000.0, 'per_unit_rate': 194.63}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27741.85, 'increment_above': 10000.0, 'per_unit_rate': 64.52}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 53978.33, 'increment_above': 50000.0, 'per_unit_rate': 47.32}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 79569.67, 'increment_above': 100000.0, 'per_unit_rate': 38.71}]}), ('Saldanha', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 9038.42, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 15378.78, 'increment_above': 2000.0, 'per_unit_rate': 327.43}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 47311.7, 'increment_above': 10000.0, 'per_unit_rate': 103.23}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 90322.33, 'increment_above': 50000.0, 'per_unit_rate': 27.97}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 111827.63, 'increment_above': 100000.0, 'per_unit_rate': 47.32}]})]
- warning: [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The Richards Bay rate above 100,000 tons is misrepresented: the source prints a base of 103,999.70 plus 21.50 per additional 100 tons or part thereof above 100,000. The proposal instead gives 21.50 as the increment rate per unit but labels the increment as above 100,000 without retaining the source's per-100-ton unit, which makes the charge basis incorrect if interpreted as per ton.
- (material) Across the listed ports, the proposal states the incremental rates are per gross-tonnage unit, but the tariff explicitly says the “Plus” increment is per additional 100 ton/part thereof. For example, Richards Bay is 275.32 per additional 100 tons above 2,000, not per ton. This unit affects the amount charged.
- (minor) The proposal omits that the craft type and number allocated for a service are decided by the port, and that the per-service tariff applies to tug/vessel assistance within the confines of the port.
- (material) The proposal states the 50% additional-tug surcharge as applying to an additional tug/vessel provided at the master's request or when deemed necessary by the Harbour Master, but does not preserve that it is 50% payable per tug. The charge can therefore be understated when multiple additional tugs are provided.
- (material) The proposal's first late-arrival/departure modifier says the 8,050.76 fee applies to all ports excluding Saldanha but does not specify the tariff's basis: per tug per half hour or part thereof. That omitted time unit changes the charge.
- (material) The proposal gives Saldanha's late arrival/departure amount as 10,152.19 but omits that it is per tug per half hour or part thereof, as stated in the tariff.
- (material) The proposal omits the separately stated tug standby hourly rates and caps for services remaining/coming on duty outside ordinary working hours: first 12 hours, following 12 hours up to 24 hours, maximums for 12/24 hours, and thereafter hourly rates. Those are applicable towage/attendance charges and affect billed amounts.
- (minor) The tariff says salvage conditions apply to tugs/vessels involved in salvage and reserves the Authority's right to claim a salvage reward; this condition is absent from the proposal.

#### vts — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) [All ports excluding Durban and Saldanha Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) [All ports excluding Durban and Saldanha Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: valid
    - (warning) [Richards Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Ngqura] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 4: valid
    - (warning) [Richards Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Ngqura] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- per_port_rules: [('Richards Bay', 'per_unit', {'rate': 0.54}), ('Durban', 'per_unit', {'rate': 0.65}), ('East London', 'per_unit', {'rate': 0.54}), ('Port Elizabeth', 'per_unit', {'rate': 0.54}), ('Ngqura', 'per_unit', {'rate': 0.54}), ('Mossel Bay', 'per_unit', {'rate': 0.54}), ('Cape Town', 'per_unit', {'rate': 0.54}), ('Saldanha Bay', 'per_unit', {'rate': 0.65})]
- warning: [Richards Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Ngqura] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal omits the stated 15% VAT. The page header says tariffs are subject to VAT at 15%, so the amount charged is higher than the listed rate/minimum alone.
- (material) The proposal does not capture the gross-tonnage fallback: if the vessel's tonnage certificate is unavailable, the highest tonnage reflected in Lloyds Register of Shipping is accepted. This can change the tonnage used to calculate the charge.

#### pilotage — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
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
    - (warning) [Saldanha] value 886.2 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 10.49 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
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
    - (warning) [Saldanha] value 886.2 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 10.49 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: valid
    - (warning) [Richards Bay] value 30960.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 18608.61 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 4: valid
    - (warning) [Richards Bay] value 30960.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 18608.61 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- per_port_rules: [('Richards Bay', 'base_plus_increment', {'base': 30960.46, 'rate': 10.93}), ('Durban', 'base_plus_increment', {'base': 18608.61, 'rate': 9.72}), ('Port Elizabeth / Ngqura', 'base_plus_increment', {'base': 8970.0, 'rate': 14.33}), ('Cape Town', 'base_plus_increment', {'base': 6342.39, 'rate': 10.2}), ('Saldanha', 'base_plus_increment', {'base': 9673.57, 'rate': 13.66}), ('Other', 'base_plus_increment', {'base': 6547.45, 'rate': 10.49})]
- warning: [Richards Bay] value 30960.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 18608.61 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 8970.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 14.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 6342.39 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 10.2 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 9673.57 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal omits the tariff's 15% VAT, although the source states these tariffs are subject to VAT. The amount charged therefore needs this tax applied in addition to the listed rates.
- (material) The marine-services incentive modifier does not give the applicable thresholds or maximum discounted calls: the source specifies 500 threshold/1,500 maximum for container vessels, and 100 threshold/300 maximum for auto carriers, break bulk, dry bulk and liquid bulk. These limits change the discount and resulting charge.

#### berthing_services — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) [Richards Bay] value 3175.89 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 13.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 3838.62 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 18.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 3052.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 14.92 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 4006.34 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 16.97 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 2801.91 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 13.68 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) [Richards Bay] value 3175.89 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 13.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 3838.62 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 18.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 3052.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 14.92 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 4006.34 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 16.97 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 2801.91 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 13.68 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: valid
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
  - attempt 4: valid
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

### Disagreements
- **light_dues**: The proposal applies the R117.08-per-100-tons tariff to all vessels as though it were a per-call charge. The source lists a separate rate for self-propelled vessels and vessels licensed by the Department of Environmental Affairs and Tourism at their registered port: R24.64 per metre or part thereof of length overall per financial year or part thereof. This rate and its applicability are missing from the proposal.; The proposal omits the explicit condition that vessels remaining within a specific port for extended periods are charged only once and are not affected by length of stay. This may affect the charge for such vessels.
- **port_dues**: The proposal omits the explicit applicability condition that these port dues are payable by vessels entering the port from passing the entrance inward until passing it outward, and also by vessels taking in bunkers at the designated anchorage and vessels at offshore moorings or similar facilities. This is part of the charge's charging scope, not just its label.; The proposal misstates the surcharge trigger as vessels that are not engaged in cargo working OR undergoing repairs. The source says vessels in port longer than 30 days that are not engaged in cargo working OR undergoing repairs will be liable; this means the exclusion applies when the vessel is undergoing repairs, and the surcharge is for those neither cargo-working nor undergoing repairs.; The proposal leaves the surcharge base as the 'incremental port-dues fee,' but the source says a 20% surcharge on the incremental fee of port dues; its interaction with the 35% reduction is not stated as the proposal's wording may imply. This needs to preserve the source's stated base rather than imply that the incremental amount is necessarily the post-reduction fee.
- **towage**: The Richards Bay rate above 100,000 tons is misrepresented: the source prints a base of 103,999.70 plus 21.50 per additional 100 tons or part thereof above 100,000. The proposal instead gives 21.50 as the increment rate per unit but labels the increment as above 100,000 without retaining the source's per-100-ton unit, which makes the charge basis incorrect if interpreted as per ton.; Across the listed ports, the proposal states the incremental rates are per gross-tonnage unit, but the tariff explicitly says the “Plus” increment is per additional 100 ton/part thereof. For example, Richards Bay is 275.32 per additional 100 tons above 2,000, not per ton. This unit affects the amount charged.; The proposal states the 50% additional-tug surcharge as applying to an additional tug/vessel provided at the master's request or when deemed necessary by the Harbour Master, but does not preserve that it is 50% payable per tug. The charge can therefore be understated when multiple additional tugs are provided.; The proposal's first late-arrival/departure modifier says the 8,050.76 fee applies to all ports excluding Saldanha but does not specify the tariff's basis: per tug per half hour or part thereof. That omitted time unit changes the charge.; The proposal gives Saldanha's late arrival/departure amount as 10,152.19 but omits that it is per tug per half hour or part thereof, as stated in the tariff.; The proposal omits the separately stated tug standby hourly rates and caps for services remaining/coming on duty outside ordinary working hours: first 12 hours, following 12 hours up to 24 hours, maximums for 12/24 hours, and thereafter hourly rates. Those are applicable towage/attendance charges and affect billed amounts.
- **vts**: The proposal omits the stated 15% VAT. The page header says tariffs are subject to VAT at 15%, so the amount charged is higher than the listed rate/minimum alone.; The proposal does not capture the gross-tonnage fallback: if the vessel's tonnage certificate is unavailable, the highest tonnage reflected in Lloyds Register of Shipping is accepted. This can change the tonnage used to calculate the charge.
- **pilotage**: The proposal omits the tariff's 15% VAT, although the source states these tariffs are subject to VAT. The amount charged therefore needs this tax applied in addition to the listed rates.; The marine-services incentive modifier does not give the applicable thresholds or maximum discounted calls: the source specifies 500 threshold/1,500 maximum for container vessels, and 100 threshold/300 maximum for auto carriers, break bulk, dry bulk and liquid bulk. These limits change the discount and resulting charge.
