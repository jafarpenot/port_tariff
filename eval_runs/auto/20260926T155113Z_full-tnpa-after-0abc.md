# Extraction run — 2026-09-26T15:51:14+00:00

**PDF:** Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** full-tnpa-after-0abc

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 7 windows, 186 sections found
assemble: 32 out-of-scope sections, general_terms_found=True
light_dues: starting, context pages=[3, 5, 6, 7, 8, 9] sections=['1', '1.1', '1.1.1']
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: done
port_dues: starting, context pages=[3, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26] sections=['SECTION 4', '4.1', '4.3', '4.1.1', '4.1.2', '4.2']
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: done
towage: starting, context pages=[3, 12, 15, 16, 17, 18] sections=['3', '3.1', '3.2', '3.6', '3.7']
towage: validate -> invalid
towage: validate -> valid
towage: verify -> material finding
towage: validate -> invalid
towage: validate -> invalid
towage: validate -> invalid
towage: done
vts: starting, context pages=[3, 11, 21, 24] sections=['2', '2.1', '2.1.1', '4.2', 'SECTION 4']
vts: validate -> invalid
vts: validate -> valid
vts: verify -> material finding
vts: validate -> valid
vts: verify -> material finding
vts: done
pilotage: starting, context pages=[3, 12, 13, 14] sections=['3', '3.1', '3.2', '3.3', '3.5']
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: validate -> invalid
pilotage: SYSTEM_ERROR — ValidationError: 1 validation error for ChargeExtraction
proposed_rule.pricing
  Value error, selected shape 'per_unit' is missing required fields: PerUnitShape(selected=True, rate=None) [type=value_error, input_value={'per_unit': {'selected':...ne, 'daily_rate': None}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
pilotage: done
berthing_services: starting, context pages=[3, 12, 18, 19] sections=['3', '3.1', '3.2', '3.8', '3.9']
berthing_services: validate -> invalid
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: validate -> invalid
berthing_services: validate -> valid
berthing_services: verify -> clean
berthing_services: done
```


## Final report — duration 2165.7s

### Identity
```
{'authority': 'Transnet National Ports Authority', 'jurisdiction': 'South Africa', 'ports': [], 'schedule_name': 'Port Tariffs', 'effective_from': '1 April 2024', 'effective_to': '31 March 2025', 'currency': 'ZAR'}
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
- (material) The rate is stated as 117.08 per 100 tons or part thereof, but the proposal records it as a per-unit gross-tonnage rate without preserving the 100-ton unit. That changes the charge if interpreted as 117.08 per ton.
- (material) The proposal omits the applicable 15% VAT. The page header states that tariffs are subject to VAT at 15%, which increases the amount charged.

#### port_dues — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) value 2.82 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) value 2.82 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- pricing_type: 'per_unit' params: {'rate': 2.82}
- warning: value 2.82 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal models the charge as a single per-call rate of 2.82 with no time tiers, but the tariff states the rates are per metre (or part thereof) of length overall per day (or part thereof), and specifies subsequent tiers of 5.56 and 11.14, plus 33.45 after 12 months. The charge must reflect those time-based tiers and units, rather than treating 2.82 as a complete flat per-call amount.

#### towage — outcome=mapped status=extraction_failed
repair_attempts=3 verify_rounds=1
- validation history:
  - attempt 1: invalid
    - (hard) cited page 30 does not exist in this document (1..27).
  - attempt 2: valid
    - (warning) value 47.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: invalid
    - (hard) outcome is 'mapped' with varies_by_port=true but per_port_rules is empty.
  - attempt 4: invalid
    - (hard) outcome is 'mapped' with varies_by_port=true but per_port_rules is empty.
  - attempt 5: invalid
    - (hard) cited page 31 does not exist in this document (1..27).
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
- per_port_rules: [('Richards Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7001.67, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 13020.67, 'increment_above': 2000.0, 'per_unit_rate': 275.32}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 39999.88, 'increment_above': 10000.0, 'per_unit_rate': 101.08}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 79999.76, 'increment_above': 50000.0, 'per_unit_rate': 30.11}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 103999.7, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Durban', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 8140.0, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 12633.99, 'increment_above': 2000.0, 'per_unit_rate': 268.99}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 38494.51, 'increment_above': 10000.0, 'per_unit_rate': 84.95}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 73118.07, 'increment_above': 50000.0, 'per_unit_rate': 32.24}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 93548.13, 'increment_above': 100000.0, 'per_unit_rate': 23.65}]}), ('East London', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5622.16, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 200.97}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27956.91, 'increment_above': 10000.0, 'per_unit_rate': 66.67}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 55913.82, 'increment_above': 50000.0, 'per_unit_rate': 25.8}]}), ('Port Elizabeth / Ngqura', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7206.98, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 11168.45, 'increment_above': 2000.0, 'per_unit_rate': 237.53}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 32257.98, 'increment_above': 10000.0, 'per_unit_rate': 73.1}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 64515.95, 'increment_above': 50000.0, 'per_unit_rate': 21.5}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 82542.46, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Mossel Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 6316.53, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 173.37}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 25806.37, 'increment_above': 10000.0, 'per_unit_rate': 60.21}]}), ('Cape Town', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5411.47, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 7898.57, 'increment_above': 2000.0, 'per_unit_rate': 194.63}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27741.85, 'increment_above': 10000.0, 'per_unit_rate': 64.52}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 53978.33, 'increment_above': 50000.0, 'per_unit_rate': 47.32}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 79569.67, 'increment_above': 100000.0, 'per_unit_rate': 38.71}]}), ('Saldanha', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 9038.42, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 15378.78, 'increment_above': 2000.0, 'per_unit_rate': 327.43}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 47311.7, 'increment_above': 10000.0, 'per_unit_rate': 103.23}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 90322.33, 'increment_above': 50000.0, 'per_unit_rate': 27.97}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 111827.63, 'increment_above': 100000.0, 'per_unit_rate': 47.32}]})]
- warning: [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposed rate and pricing shape do not match the towage tariff. The general tug/vessel assistance charge is priced per service based on vessel tonnage, with different basic and incremental rates by port and tonnage band; the source does not state a flat rate of 47 per metre of LOA. It also specifies separate hourly tug/standby charges and applicable surcharges/conditions. Section 4.8 on page 15 only says tugs used in oil-pollution combating are charged separately; it does not establish the general towage rate.

#### vts — outcome=not_present status=-
repair_attempts=1 verify_rounds=1
- validation history:
  - attempt 1: invalid
    - (hard) cited page 41 does not exist in this document (1..27).
    - (hard) cited page 42 does not exist in this document (1..27).
    - (hard) cited page 47 does not exist in this document (1..27).
    - (hard) cited page 48 does not exist in this document (1..27).
  - attempt 2: valid
  - attempt 3: valid
- (material) The proposal's not_present outcome is incorrect: Section 2.1.1 explicitly sets VTS charges per GT per port call (0.54 at all ports except Durban and Saldanha Bay; 0.65 at Durban and Saldanha Bay), with a minimum fee of 235.52. The outcome should represent a present VTS charge, not an absent charge.

#### pilotage — outcome=? status=system_error
repair_attempts=0 verify_rounds=0
- validation history:
  - attempt 1: valid
  - attempt 2: invalid
    - (hard) outcome is 'mapped' with varies_by_port=true but per_port_rules is empty.

#### berthing_services — outcome=mapped status=-
repair_attempts=2 verify_rounds=1
- validation history:
  - attempt 1: invalid
    - (hard) cited page 35 does not exist in this document (1..27).
    - (hard) cited page 36 does not exist in this document (1..27).
    - (hard) cited page 37 does not exist in this document (1..27).
    - (hard) cited page 38 does not exist in this document (1..27).
  - attempt 2: valid
    - (warning) value 13083.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: invalid
    - (hard) cited page 36 does not exist in this document (1..27).
  - attempt 4: valid
- per_port_rules: [('Saldanha', 'per_unit', {'rate': 1.15})]
- (minor) The proposal cites page 12, but the supplied source page identifies itself as printed page 24 (Tariff Book April 2024–March 2025). The rate and condition do appear there; the page citation is incorrect.

### Disagreements
- **light_dues**: The rate is stated as 117.08 per 100 tons or part thereof, but the proposal records it as a per-unit gross-tonnage rate without preserving the 100-ton unit. That changes the charge if interpreted as 117.08 per ton.; The proposal omits the applicable 15% VAT. The page header states that tariffs are subject to VAT at 15%, which increases the amount charged.
- **port_dues**: The proposal models the charge as a single per-call rate of 2.82 with no time tiers, but the tariff states the rates are per metre (or part thereof) of length overall per day (or part thereof), and specifies subsequent tiers of 5.56 and 11.14, plus 33.45 after 12 months. The charge must reflect those time-based tiers and units, rather than treating 2.82 as a complete flat per-call amount.
- **vts**: The proposal's not_present outcome is incorrect: Section 2.1.1 explicitly sets VTS charges per GT per port call (0.54 at all ports except Durban and Saldanha Bay; 0.65 at Durban and Saldanha Bay), with a minimum fee of 235.52. The outcome should represent a present VTS charge, not an absent charge.
