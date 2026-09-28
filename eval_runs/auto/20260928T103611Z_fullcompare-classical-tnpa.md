# Extraction run — 2026-09-28T10:36:11+00:00

**PDF:** /Users/jafarpenot/Desktop/my_projs/port_tariff/Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** fullcompare-classical-tnpa

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
structure_scan: 1762 chars
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 9 windows, 142 sections found
assemble: 32 out-of-scope sections, general_terms_found=True
light_dues: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19] sections=['6', '1', '1.1', '1.1.1']
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: done
port_dues: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] sections=['6', '4', '4.1', '4.1.1', '4.1.2', '4.2']
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: done
towage: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] sections=['3', '3.1', '3.2', '3.6', '3.9', '4.8', '4', '4.1']
towage: validate -> invalid
towage: validate -> valid
towage: verify -> material finding
towage: validate -> invalid
towage: validate -> valid
towage: verify -> material finding
towage: done
vts: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] sections=['6', '2', '2.1', '2.1.1']
vts: validate -> valid
vts: verify -> material finding
vts: validate -> valid
vts: verify -> clean
vts: done
pilotage: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18, 19] sections=['6', '3', '3.1', '3.2', '3.3', '3.5']
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: done
berthing_services: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] sections=['3', '3.1', '3.2', '3.8', '3.9']
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: done
```


## Final report — duration 1699.1s

### Identity
```
{'authority': 'Transnet National Ports Authority', 'jurisdiction': 'South African ports', 'ports': [], 'schedule_name': 'Port Tariffs', 'effective_from': '2024-04-01', 'effective_to': '2025-03-31', 'currency': 'ZAR'}
```
is_new_edition=True matched_existing_authority=Transnet National Ports Authority

### Coverage
- pages_read: 27/27
- general_terms_found: True
- out_of_scope_sections: 32

### Charges
#### light_dues — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
    - (warning) value 117.08 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- pricing_type: 'per_unit' params: {'rate': 117.08}
- warning: value 117.08 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The mapped rate is not represented with the source's billing unit: the tariff is 117.08 per 100 tons or part thereof, not 117.08 per gross ton. As written, the per_unit/gross_tonnage rate can produce a charge 100 times too high unless its unit is explicitly encoded as 100-ton blocks.
- (material) The proposal omits the coaster tariff treatment. The source says coaster light dues are payable under a special agreement, bona fide coasters are charged monthly, and a bona fide coaster arriving from a foreign port pays full light dues at the first South African port. These rules change the amount/applicability and are not included among the listed modifiers.

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
    - (warning) value -100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- pricing_type: 'base_plus_increment_times_duration' params: {'basic_rate': 192.73, 'daily_rate': 57.79}
- warning: value 192.73 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value 57.79 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -35.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value 20.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -60.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -10.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -15.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal omits that the printed port-dues tariffs are subject to 15% VAT. Its stated basic_rate and daily_rate therefore do not represent the full amount charged unless VAT is added separately.
- (material) The proposal gives gross tonnage as the basis but omits the tariff's unit: both the basic and incremental rates are charged per 100 tons or part thereof. Applying the rates directly to gross tonnage without charging for each 100-ton unit (including a partial unit) would produce a different amount.
- (material) The daily increment is not simply a daily amount for each whole day: the source specifies each 24-hour period, with a part of a 24-hour period applied pro rata. The proposal does not preserve that proration rule, which can change the incremental charge for a partial period.
- (material) The proposal does not state the charge's applicability period and included cases: port dues run from the vessel passing the port entrance inward until passing it outward, and the source also makes vessels taking in bunkers at the designated anchorage liable. This omission can change when and to which vessels the charge applies.

#### towage — outcome=mapped status=-
repair_attempts=2 verify_rounds=1
- validation history:
  - attempt 1: invalid
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
    - (hard) [East London] the final band's max_inclusive must be null (open-ended).
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Mossel Bay] the final band's max_inclusive must be null (open-ended).
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
  - attempt 4: valid
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
- per_port_rules: [('Richards Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7001.67, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 13020.67, 'increment_above': 2000.0, 'per_unit_rate': 275.32}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 39999.88, 'increment_above': 10000.0, 'per_unit_rate': 101.08}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 79999.76, 'increment_above': 50000.0, 'per_unit_rate': 30.11}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 103999.7, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Durban', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 8140.0, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 12633.99, 'increment_above': 2000.0, 'per_unit_rate': 268.99}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 38494.51, 'increment_above': 10000.0, 'per_unit_rate': 84.95}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 73118.07, 'increment_above': 50000.0, 'per_unit_rate': 32.24}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 93548.13, 'increment_above': 100000.0, 'per_unit_rate': 23.65}]}), ('East London', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5622.16, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 200.97}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27956.91, 'increment_above': 10000.0, 'per_unit_rate': 66.67}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 55913.82, 'increment_above': 50000.0, 'per_unit_rate': 25.8}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 55913.82, 'increment_above': 50000.0, 'per_unit_rate': 25.8}]}), ('Port Elizabeth / Ngqura', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7206.98, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 11168.45, 'increment_above': 2000.0, 'per_unit_rate': 237.53}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 32257.98, 'increment_above': 10000.0, 'per_unit_rate': 73.1}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 64515.95, 'increment_above': 50000.0, 'per_unit_rate': 21.5}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 82542.46, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Mossel Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 6316.53, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 173.37}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 25806.37, 'increment_above': 10000.0, 'per_unit_rate': 60.21}, {'min_exclusive': 50000.0, 'max_inclusive': None, 'base': 25806.37, 'increment_above': 10000.0, 'per_unit_rate': 60.21}]}), ('Cape Town', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5411.47, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 7898.57, 'increment_above': 2000.0, 'per_unit_rate': 194.63}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27741.85, 'increment_above': 10000.0, 'per_unit_rate': 64.52}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 53978.33, 'increment_above': 50000.0, 'per_unit_rate': 47.32}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 79569.67, 'increment_above': 100000.0, 'per_unit_rate': 38.71}]}), ('Saldanha', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 9038.42, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 15378.78, 'increment_above': 2000.0, 'per_unit_rate': 327.43}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 47311.7, 'increment_above': 10000.0, 'per_unit_rate': 103.23}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 90322.33, 'increment_above': 50000.0, 'per_unit_rate': 27.97}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 111827.63, 'increment_above': 100000.0, 'per_unit_rate': 47.32}]})]
- warning: [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal incorrectly carries the per-100-ton increment into Richards Bay's 'Above 100 000' band as 21.50. The source table prints 23.65 per 100 tons or part thereof above 100,000 for Richards Bay; 21.50 is the Port Elizabeth/Ngqura value. This changes the charge for Richards Bay vessels over 100,000 tons.
- (material) The proposal's towage modifier says a late-arrival/departure fee of 8,050.76 applies at every port, but the source explicitly gives that amount for all ports excluding Saldanha and separately sets Saldanha at 10,152.19. The proposal gets the Saldanha fee wrong.
- (material) East London's 'Above 100 000' band is incorrectly represented using the previous band's 50,000-plus increment of 25.80 from a base at 50,000. The source marks the 50,001–100,000 East London entries n/a and the Above 100,000 East London entry n/a, so that port has no such banded towage rate in this table.
- (material) Mossel Bay's proposal extends the 10,000–50,000 rate structure (base 25,806.37 plus 60.21 per 100 tons above 10,000) to all tonnages above 50,000. The source marks the 50,001–100,000 and Above 100,000 Mossel Bay rates n/a; the proposal therefore invents an applicable rate for higher-tonnage vessels.
- (material) The proposal's Mossel Bay 10,000–50,000 base is 25,806.37, but the table's Mossel Bay column is 25,806.37; however, the 50,000-plus carry-forward shown in the proposal conflicts with n/a entries. [Do not report this duplicate concern.]
- (material) Port Elizabeth/Ngqura's 50,001–100,000 per-100-ton increment is incorrectly given as 21.50. The source prints 21.50 in the 50,001–100,000 row for Richards Bay? Wait source order: Richards Bay 30.11, Durban 32.24, East London 25.80, Port Elizabeth/Ngqura 21.50, Mossel Bay n/a, Cape Town 47.32, Saldanha 27.97. Proposal's Port Elizabeth value 21.50 correct.

#### vts — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) [all ports excluding Durban and Saldanha Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) [Richards Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Ngqura] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- per_port_rules: [('Richards Bay', 'per_unit', {'rate': 0.54}), ('East London', 'per_unit', {'rate': 0.54}), ('Ngqura', 'per_unit', {'rate': 0.54}), ('Port Elizabeth', 'per_unit', {'rate': 0.54}), ('Mossel Bay', 'per_unit', {'rate': 0.54}), ('Cape Town', 'per_unit', {'rate': 0.54}), ('Durban', 'per_unit', {'rate': 0.65}), ('Saldanha Bay', 'per_unit', {'rate': 0.65})]
- warning: [Richards Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [East London] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Ngqura] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Mossel Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.

#### pilotage — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
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
  - attempt 2: valid
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
- per_port_rules: [('Richards Bay', 'base_plus_increment', {'base': 30960.46, 'rate': 10.93}), ('Durban', 'base_plus_increment', {'base': 18608.61, 'rate': 9.72}), ('Port Elizabeth / Ngqura', 'base_plus_increment', {'base': 8970.0, 'rate': 14.33}), ('Cape Town', 'base_plus_increment', {'base': 6342.39, 'rate': 10.2}), ('Saldanha', 'base_plus_increment', {'base': 9673.57, 'rate': 13.66}), ('Other', 'base_plus_increment', {'base': 6547.45, 'rate': 10.49})]
- warning: [Richards Bay] value 30960.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 10.93 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 18608.61 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 9.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
- warning: [Saldanha] value 13.66 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 10.49 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The Saldanha tanker-stay pilot-on-board duty is an hourly charge of R886.20, but the proposal records it only as a modifier and omits the amount. This is a separate charge that affects the amount billed.
- (material) The proposal refers to the national incentive but does not encode its actual discount schedule. Page 6 sets out vessel/cargo thresholds, discount steps, and maximum eligible calls (for example, container vessels: threshold 500, 1% per 50 calls above threshold, maximum 1,500 calls). Omitting these values can change the pilotage charge.
- (material) The tariff rates are subject to 15% VAT, as stated on the tariff pages, but the proposal does not record or otherwise account for VAT.
- (material) The +50% after-hours trigger is stated without the port-specific ordinary-hours schedule. Page 6 defines different hours for Mossel Bay and East London, while Richards Bay, Durban, Ngqura, Port Elizabeth, Cape Town, and Saldanha have 24-hour service; the missing schedule can change when the surcharge applies, particularly for the proposal's grouped “Other” ports.

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
- (material) The per-port rate rules omit the source's rate unit: the incremental amounts are charged per 100 tons or part thereof, not simply per gross-tonnage unit. Without that 100-ton increment/rounding condition, applying the listed rates can materially miscalculate the service charge.
- (material) The proposal omits the tariff's VAT treatment. The source page states that tariffs are subject to VAT at 15%, which changes the amount payable when VAT is applicable.

### Disagreements
- **light_dues**: The mapped rate is not represented with the source's billing unit: the tariff is 117.08 per 100 tons or part thereof, not 117.08 per gross ton. As written, the per_unit/gross_tonnage rate can produce a charge 100 times too high unless its unit is explicitly encoded as 100-ton blocks.; The proposal omits the coaster tariff treatment. The source says coaster light dues are payable under a special agreement, bona fide coasters are charged monthly, and a bona fide coaster arriving from a foreign port pays full light dues at the first South African port. These rules change the amount/applicability and are not included among the listed modifiers.
- **port_dues**: The proposal omits that the printed port-dues tariffs are subject to 15% VAT. Its stated basic_rate and daily_rate therefore do not represent the full amount charged unless VAT is added separately.; The proposal gives gross tonnage as the basis but omits the tariff's unit: both the basic and incremental rates are charged per 100 tons or part thereof. Applying the rates directly to gross tonnage without charging for each 100-ton unit (including a partial unit) would produce a different amount.; The daily increment is not simply a daily amount for each whole day: the source specifies each 24-hour period, with a part of a 24-hour period applied pro rata. The proposal does not preserve that proration rule, which can change the incremental charge for a partial period.; The proposal does not state the charge's applicability period and included cases: port dues run from the vessel passing the port entrance inward until passing it outward, and the source also makes vessels taking in bunkers at the designated anchorage liable. This omission can change when and to which vessels the charge applies.
- **towage**: The proposal incorrectly carries the per-100-ton increment into Richards Bay's 'Above 100 000' band as 21.50. The source table prints 23.65 per 100 tons or part thereof above 100,000 for Richards Bay; 21.50 is the Port Elizabeth/Ngqura value. This changes the charge for Richards Bay vessels over 100,000 tons.; The proposal's towage modifier says a late-arrival/departure fee of 8,050.76 applies at every port, but the source explicitly gives that amount for all ports excluding Saldanha and separately sets Saldanha at 10,152.19. The proposal gets the Saldanha fee wrong.; East London's 'Above 100 000' band is incorrectly represented using the previous band's 50,000-plus increment of 25.80 from a base at 50,000. The source marks the 50,001–100,000 East London entries n/a and the Above 100,000 East London entry n/a, so that port has no such banded towage rate in this table.; Mossel Bay's proposal extends the 10,000–50,000 rate structure (base 25,806.37 plus 60.21 per 100 tons above 10,000) to all tonnages above 50,000. The source marks the 50,001–100,000 and Above 100,000 Mossel Bay rates n/a; the proposal therefore invents an applicable rate for higher-tonnage vessels.; The proposal's Mossel Bay 10,000–50,000 base is 25,806.37, but the table's Mossel Bay column is 25,806.37; however, the 50,000-plus carry-forward shown in the proposal conflicts with n/a entries. [Do not report this duplicate concern.]; Port Elizabeth/Ngqura's 50,001–100,000 per-100-ton increment is incorrectly given as 21.50. The source prints 21.50 in the 50,001–100,000 row for Richards Bay? Wait source order: Richards Bay 30.11, Durban 32.24, East London 25.80, Port Elizabeth/Ngqura 21.50, Mossel Bay n/a, Cape Town 47.32, Saldanha 27.97. Proposal's Port Elizabeth value 21.50 correct.
- **pilotage**: The Saldanha tanker-stay pilot-on-board duty is an hourly charge of R886.20, but the proposal records it only as a modifier and omits the amount. This is a separate charge that affects the amount billed.; The proposal refers to the national incentive but does not encode its actual discount schedule. Page 6 sets out vessel/cargo thresholds, discount steps, and maximum eligible calls (for example, container vessels: threshold 500, 1% per 50 calls above threshold, maximum 1,500 calls). Omitting these values can change the pilotage charge.; The tariff rates are subject to 15% VAT, as stated on the tariff pages, but the proposal does not record or otherwise account for VAT.; The +50% after-hours trigger is stated without the port-specific ordinary-hours schedule. Page 6 defines different hours for Mossel Bay and East London, while Richards Bay, Durban, Ngqura, Port Elizabeth, Cape Town, and Saldanha have 24-hour service; the missing schedule can change when the surcharge applies, particularly for the proposal's grouped “Other” ports.
- **berthing_services**: The per-port rate rules omit the source's rate unit: the incremental amounts are charged per 100 tons or part thereof, not simply per gross-tonnage unit. Without that 100-ton increment/rounding condition, applying the listed rates can materially miscalculate the service charge.; The proposal omits the tariff's VAT treatment. The source page states that tariffs are subject to VAT at 15%, which changes the amount payable when VAT is applicable.
