# Extraction run — 2026-09-25T17:58:06+00:00

**PDF:** Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** full-tnpa-linear-pipeline

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 7 windows, 182 sections found
assemble: 24 out-of-scope sections, general_terms_found=True
light_dues: starting
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: validate -> invalid
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: done
port_dues: starting
port_dues: validate -> invalid
port_dues: validate -> invalid
port_dues: validate -> invalid
port_dues: validate -> invalid
port_dues: done
towage: starting
towage: validate -> invalid
towage: validate -> invalid
towage: validate -> valid
towage: verify -> material finding
towage: validate -> invalid
towage: validate -> valid
towage: verify -> material finding
towage: done
vts: starting
vts: validate -> invalid
vts: validate -> valid
vts: verify -> clean
vts: done
pilotage: starting
pilotage: validate -> invalid
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: done
berthing_services: starting
berthing_services: validate -> invalid
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: done
```


## Final report — duration 4937.3s

### Identity
```
{'authority': 'Transnet National Ports Authority', 'jurisdiction': 'South Africa', 'ports': [], 'schedule_name': 'Port Tariffs', 'effective_from': '2024-04-01', 'effective_to': '2025-03-31', 'currency': 'ZAR'}
```
is_new_edition=True matched_existing_authority=Transnet National Ports Authority

### Coverage
- pages_read: 27/27
- general_terms_found: True
- out_of_scope_sections: 24

### Charges
#### light_dues — outcome=mapped status=-
repair_attempts=1 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: invalid
    - (hard) Unknown basis 'gross tonnage'
    - (hard) Unknown rounding mode 'ceiling'
    - (hard) Unknown multiplicity 'once_per_call'
  - attempt 3: valid
- pricing_type: 'per_unit' params: {'rate': 117.08}
- (material) The proposal omits the separate light-dues tariff for self-propelled vessels and vessels licensed by the Department of Environmental Affairs and Tourism at their registered port: 24.64 per metre or part thereof of length overall per financial year or part thereof. The proposed gross-tonnage rule does not cover these vessels.
- (material) For the 117.08 rate, the source specifies “per 100 tons or part thereof,” not simply per gross-tonnage unit. The proposal does not preserve the 100-ton charging unit, so it can yield a different charge if the rate is applied per ton.
- (material) The source says light dues are raised at the first South African port of call and remain valid through the last South African port of call, subject to staying within South African waters and a 60-day limit; after 60 days, dues are raised per calendar month, and the vessel may request coastal status within the 60-day window. The proposal's unqualified per_call multiplicity omits these applicability and repeat-charge conditions.

#### port_dues — outcome=mapped status=extraction_failed
repair_attempts=3 verify_rounds=0
- validation history:
  - attempt 1: invalid
    - (hard) Unknown basis 'gross tonnage, per 100 tons or part thereof'
    - (hard) Unknown rounding mode 'up'
  - attempt 2: invalid
    - (hard) Unknown multiplicity 'once_per_call'
  - attempt 3: invalid
    - (hard) Unknown basis 'gross tonnage, charged per 100 tons or part thereof'
    - (hard) Unknown rounding mode 'up'
  - attempt 4: invalid
    - (hard) Unknown multiplicity 'once_per_call'
- pricing_type: 'base_plus_increment' params: {'base': 192.73, 'rate': 57.79}

#### towage — outcome=mapped status=-
repair_attempts=3 verify_rounds=1
- validation history:
  - attempt 1: invalid
    - (hard) [Richards Bay] Unknown rounding mode 'up'
    - (hard) [Durban] Unknown rounding mode 'up'
    - (hard) [East London] Unknown rounding mode 'up'
    - (hard) [East London] the final band's max_inclusive must be null (open-ended).
    - (hard) [Port Elizabeth / Ngqura] Unknown rounding mode 'up'
    - (hard) [Mossel Bay] Unknown rounding mode 'up'
    - (hard) [Mossel Bay] the final band's max_inclusive must be null (open-ended).
    - (hard) [Cape Town] Unknown rounding mode 'up'
    - (hard) [Saldanha Bay] Unknown rounding mode 'up'
  - attempt 2: invalid
    - (hard) [Richards Bay] Unknown basis 'vessel gross tonnage'
    - (hard) [Durban] Unknown basis 'vessel gross tonnage'
    - (hard) [East London] Unknown basis 'vessel gross tonnage'
    - (hard) [Port Elizabeth / Ngqura] Unknown basis 'vessel gross tonnage'
    - (hard) [Mossel Bay] Unknown basis 'vessel gross tonnage'
    - (hard) [Cape Town] Unknown basis 'vessel gross tonnage'
    - (hard) [Saldanha] Unknown basis 'vessel gross tonnage'
  - attempt 3: valid
  - attempt 4: invalid
    - (hard) [Richards Bay] Unknown basis 'vessel gross tonnage (GT)'
    - (hard) [Richards Bay] Unknown rounding mode 'up'
    - (hard) [Durban] Unknown basis 'vessel gross tonnage (GT)'
    - (hard) [Durban] Unknown rounding mode 'up'
    - (hard) [East London] Unknown basis 'vessel gross tonnage (GT)'
    - (hard) [East London] Unknown rounding mode 'up'
    - (hard) [East London] the final band's max_inclusive must be null (open-ended).
    - (hard) [Port Elizabeth / Ngqura] Unknown basis 'vessel gross tonnage (GT)'
    - (hard) [Port Elizabeth / Ngqura] Unknown rounding mode 'up'
    - (hard) [Mossel Bay] Unknown basis 'vessel gross tonnage (GT)'
    - (hard) [Mossel Bay] Unknown rounding mode 'up'
    - (hard) [Mossel Bay] the final band's max_inclusive must be null (open-ended).
    - (hard) [Cape Town] Unknown basis 'vessel gross tonnage (GT)'
    - (hard) [Cape Town] Unknown rounding mode 'up'
    - (hard) [Saldanha] Unknown basis 'vessel gross tonnage (GT)'
    - (hard) [Saldanha] Unknown rounding mode 'up'
  - attempt 5: valid
- per_port_rules: [('Richards Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7001.67, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 13020.67, 'increment_above': 2000.0, 'per_unit_rate': 275.32}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 39999.88, 'increment_above': 10000.0, 'per_unit_rate': 101.08}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 79999.76, 'increment_above': 50000.0, 'per_unit_rate': 30.11}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 103999.7, 'increment_above': 100000.0, 'per_unit_rate': 23.65}]}), ('Durban', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 8140.0, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 12633.99, 'increment_above': 2000.0, 'per_unit_rate': 268.99}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 38494.51, 'increment_above': 10000.0, 'per_unit_rate': 84.95}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 73118.07, 'increment_above': 50000.0, 'per_unit_rate': 32.24}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 93548.13, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('East London', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5622.16, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 200.97}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27956.91, 'increment_above': 10000.0, 'per_unit_rate': 66.67}, {'min_exclusive': 50000.0, 'max_inclusive': None, 'base': 55913.82, 'increment_above': 50000.0, 'per_unit_rate': 25.8}]}), ('Port Elizabeth / Ngqura', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7206.98, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 11168.45, 'increment_above': 2000.0, 'per_unit_rate': 237.53}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 32257.98, 'increment_above': 10000.0, 'per_unit_rate': 73.1}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 64515.95, 'increment_above': 50000.0, 'per_unit_rate': 21.5}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 82542.46, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Mossel Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 6316.53, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 173.37}, {'min_exclusive': 10000.0, 'max_inclusive': None, 'base': 25806.37, 'increment_above': 10000.0, 'per_unit_rate': 60.21}]}), ('Cape Town', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5411.47, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 7898.57, 'increment_above': 2000.0, 'per_unit_rate': 194.63}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27741.85, 'increment_above': 10000.0, 'per_unit_rate': 64.52}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 53978.33, 'increment_above': 50000.0, 'per_unit_rate': 47.32}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 79569.67, 'increment_above': 100000.0, 'per_unit_rate': 47.32}]}), ('Saldanha', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 9038.42, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 15378.78, 'increment_above': 2000.0, 'per_unit_rate': 327.43}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 47311.7, 'increment_above': 10000.0, 'per_unit_rate': 103.23}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 90322.33, 'increment_above': 50000.0, 'per_unit_rate': 27.97}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 111827.63, 'increment_above': 100000.0, 'per_unit_rate': 27.97}]})]
- (material) The proposal extends East London's 25.80-per-100-ton rate above 100,000 tons. The source lists that rate only for 50,001–100,000 tons and marks East London n/a above 100,000 tons; the proposed open-ended final band therefore applies a charge where the table gives no rate.
- (material) The proposal makes Mossel Bay's 60.21-per-100-ton band open-ended above 10,000 tons. The source gives this rate for 10,000–50,000 tons, then marks Mossel Bay n/a for both 50,001–100,000 and above 100,000 tons; extending the band past 50,000 is unsupported.
- (material) The proposed above-100,000-ton incremental rate is 21.50 for Durban, but the source marks Durban n/a in that row. This assigns a rate where none is listed.
- (material) The proposal applies Port Elizabeth / Ngqura's 21.50-per-100-ton rate above 100,000 tons. The source lists 21.50 only for 50,001–100,000 tons and marks Port Elizabeth / Ngqura n/a above 100,000 tons.
- (material) The proposal gives Saldanha an above-100,000-ton increment of 27.97 per 100 tons, but the source's above-100,000 row gives Saldanha 38.71. The proposed value appears to carry forward the 50,001–100,000 rate instead.
- (material) The proposal omits towage surcharges that change the payable amount: 25% for services commencing or terminating outside ordinary working hours; 50% per additional tug when requested by the master or deemed necessary for safety; and 50% for servicing a vessel without its own power, rising to 100% if an additional tug is provided at the master's request. The source also charges normal fees enhanced by 25% if an after-hours tug request is cancelled after standby begins.
- (material) The proposal omits the late-arrival/departure charge: if a vessel is at least 30 minutes late against its notified time, the source charges 8,050.76 per tug per half-hour or part thereof at all ports except Saldanha, where it charges 10,152.19. These charges are additional applicability/rate rules not represented in the proposed per-service bands.

#### vts — outcome=mapped status=-
repair_attempts=1 verify_rounds=0
- validation history:
  - attempt 1: invalid
    - (hard) [Richards Bay] Unknown basis 'gross tonnage (GT)'
    - (hard) [Richards Bay] Unknown rounding mode 'none'
    - (hard) [East London] Unknown basis 'gross tonnage (GT)'
    - (hard) [East London] Unknown rounding mode 'none'
    - (hard) [Ngqura] Unknown basis 'gross tonnage (GT)'
    - (hard) [Ngqura] Unknown rounding mode 'none'
    - (hard) [Port Elizabeth] Unknown basis 'gross tonnage (GT)'
    - (hard) [Port Elizabeth] Unknown rounding mode 'none'
    - (hard) [Mossel Bay] Unknown basis 'gross tonnage (GT)'
    - (hard) [Mossel Bay] Unknown rounding mode 'none'
    - (hard) [Cape Town] Unknown basis 'gross tonnage (GT)'
    - (hard) [Cape Town] Unknown rounding mode 'none'
    - (hard) [Durban] Unknown basis 'gross tonnage (GT)'
    - (hard) [Durban] Unknown rounding mode 'none'
    - (hard) [Saldanha Bay] Unknown basis 'gross tonnage (GT)'
    - (hard) [Saldanha Bay] Unknown rounding mode 'none'
  - attempt 2: valid
- per_port_rules: [('Richards Bay', 'per_unit', {'rate': 0.54}), ('East London', 'per_unit', {'rate': 0.54}), ('Ngqura', 'per_unit', {'rate': 0.54}), ('Port Elizabeth', 'per_unit', {'rate': 0.54}), ('Mossel Bay', 'per_unit', {'rate': 0.54}), ('Cape Town', 'per_unit', {'rate': 0.54}), ('Durban', 'per_unit', {'rate': 0.65}), ('Saldanha Bay', 'per_unit', {'rate': 0.65})]

#### pilotage — outcome=unmapped status=-
repair_attempts=1 verify_rounds=1
- validation history:
  - attempt 1: invalid
    - (hard) [Richards Bay] Unknown rounding mode 'ceiling'
    - (hard) [Durban] Unknown rounding mode 'ceiling'
    - (hard) [Port Elizabeth / Ngqura] Unknown rounding mode 'ceiling'
    - (hard) [Cape Town] Unknown rounding mode 'ceiling'
    - (hard) [Saldanha] Unknown rounding mode 'ceiling'
    - (hard) [Other] Unknown rounding mode 'ceiling'
  - attempt 2: valid
    - (warning) [Richards Bay] value 30960.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 10.93 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 18608.61 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 9.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 8970.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 14.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 6342.39 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 10.2 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 9673.57 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 13.66 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 10.49 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: valid
- unmapped_source_text: 'Section 3.3 (page 7): “Per Service (normal entering or leaving the port)” and “Basic Fee / Per 100 tons or part thereof” with separate rates under the port columns. “Pilotage dues for services other than normal entering or leaving the port such as towage, standing by, etc. are available on application.” “A surcharge of 50% is payable at all ports in the following instances: If the pilotage service terminates or commences outside ordinary working hours; If the vessel is not ready to be moved 30 minutes after the notified time or 30 minutes after the pilot has boarded, whichever is the later; If the request for a pilotage service is cancelled at any time within 30 minutes prior to the notified time and the pilot has not boarded.” “A surcharge of 50% is only applicable at the Port of Durban in the following instance: If the request for a pilotage service is cancelled at any time within 60 minutes prior to the notified time and the pilot has not boarded.” Section 3.2 (page 6) also states: “The following incentive applies to the service charges of pilotage, craft assistance and berthing services,” with discounts based on vessel/cargo type, calls, and thresholds. The per-service / per-100-tons tariff has port-specific rates, while the payable charge also depends on conditional surcharges and an applicable incentive; these combined rules do not fit one of the four supported pricing shapes.'
- (material) The outcome “unmapped” is not supported: page 7 gives an explicit normal pilotage tariff as a basic fee per service plus a rate per 100 tons or part thereof, with port-specific rates. The listed surcharges and the page 6 incentive are conditional adjustments to that tariff, not evidence that the underlying charge lacks a supported pricing shape; the proposal therefore wrongly leaves an extractable pilotage charge unmapped.

#### berthing_services — outcome=unmapped status=-
repair_attempts=1 verify_rounds=1
- validation history:
  - attempt 1: invalid
    - (hard) [Richards Bay] Unknown basis 'vessel service'
    - (hard) [Richards Bay] Unknown rounding mode 'none'
    - (hard) [Port Elizabeth / Ngqura] Unknown basis 'vessel service'
    - (hard) [Port Elizabeth / Ngqura] Unknown rounding mode 'none'
    - (hard) [Cape Town] Unknown basis 'vessel service'
    - (hard) [Cape Town] Unknown rounding mode 'none'
    - (hard) [Saldanha] Unknown basis 'vessel service'
    - (hard) [Saldanha] Unknown rounding mode 'none'
    - (hard) [Other Ports] Unknown basis 'vessel service'
    - (hard) [Other Ports] Unknown rounding mode 'none'
  - attempt 2: valid
    - (warning) [Richards Bay] value 3175.89 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 3838.62 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 3052.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 4006.34 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other Ports] value 2801.91 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 3: valid
- unmapped_source_text: 'Section 3.8 states that berthing-service fees are payable per service for vessels entering or leaving a port, shifting berth (including warping and shifts to/from a drydock or slipway), engine trials, remooring, and related attendance. The table gives a port-specific “Basic fee” and “Plus Per 100 tons or part thereof” rate: Richards Bay 3 175.89 + 13.46; Port Elizabeth/Ngqura 3 838.62 + 18.72; Cape Town 3 052.33 + 14.92; Saldanha 4 006.34 + 16.97; Other Ports 2 801.91 + 13.68. It further states: “A surcharge of 50% will be payable” if the service terminates or commences outside ordinary working hours; if requested berthing staff to remain/come on duty outside ordinary working hours is cancelled after standby has commenced; or if the vessel arrives or departs 30 minutes or more after the notified time. The conditional surcharge is not representable in the available pricing-rule shapes. (Section 3.8, page 9.)'
- (material) The proposal marks this charge unmapped even though the source gives a standard, quantifiable rate: a port-specific basic fee plus a fee per 100 tons or part thereof. That is a base-plus-tonnage pricing rule; the conditional 50% surcharge does not make the underlying charge unpriceable. The source’s surcharge conditions can be retained as modifiers rather than treating the whole charge as unmapped.

### Disagreements
- **light_dues**: The proposal omits the separate light-dues tariff for self-propelled vessels and vessels licensed by the Department of Environmental Affairs and Tourism at their registered port: 24.64 per metre or part thereof of length overall per financial year or part thereof. The proposed gross-tonnage rule does not cover these vessels.; For the 117.08 rate, the source specifies “per 100 tons or part thereof,” not simply per gross-tonnage unit. The proposal does not preserve the 100-ton charging unit, so it can yield a different charge if the rate is applied per ton.; The source says light dues are raised at the first South African port of call and remain valid through the last South African port of call, subject to staying within South African waters and a 60-day limit; after 60 days, dues are raised per calendar month, and the vessel may request coastal status within the 60-day window. The proposal's unqualified per_call multiplicity omits these applicability and repeat-charge conditions.
- **towage**: The proposal extends East London's 25.80-per-100-ton rate above 100,000 tons. The source lists that rate only for 50,001–100,000 tons and marks East London n/a above 100,000 tons; the proposed open-ended final band therefore applies a charge where the table gives no rate.; The proposal makes Mossel Bay's 60.21-per-100-ton band open-ended above 10,000 tons. The source gives this rate for 10,000–50,000 tons, then marks Mossel Bay n/a for both 50,001–100,000 and above 100,000 tons; extending the band past 50,000 is unsupported.; The proposed above-100,000-ton incremental rate is 21.50 for Durban, but the source marks Durban n/a in that row. This assigns a rate where none is listed.; The proposal applies Port Elizabeth / Ngqura's 21.50-per-100-ton rate above 100,000 tons. The source lists 21.50 only for 50,001–100,000 tons and marks Port Elizabeth / Ngqura n/a above 100,000 tons.; The proposal gives Saldanha an above-100,000-ton increment of 27.97 per 100 tons, but the source's above-100,000 row gives Saldanha 38.71. The proposed value appears to carry forward the 50,001–100,000 rate instead.; The proposal omits towage surcharges that change the payable amount: 25% for services commencing or terminating outside ordinary working hours; 50% per additional tug when requested by the master or deemed necessary for safety; and 50% for servicing a vessel without its own power, rising to 100% if an additional tug is provided at the master's request. The source also charges normal fees enhanced by 25% if an after-hours tug request is cancelled after standby begins.; The proposal omits the late-arrival/departure charge: if a vessel is at least 30 minutes late against its notified time, the source charges 8,050.76 per tug per half-hour or part thereof at all ports except Saldanha, where it charges 10,152.19. These charges are additional applicability/rate rules not represented in the proposed per-service bands.
- **pilotage**: The outcome “unmapped” is not supported: page 7 gives an explicit normal pilotage tariff as a basic fee per service plus a rate per 100 tons or part thereof, with port-specific rates. The listed surcharges and the page 6 incentive are conditional adjustments to that tariff, not evidence that the underlying charge lacks a supported pricing shape; the proposal therefore wrongly leaves an extractable pilotage charge unmapped.
- **berthing_services**: The proposal marks this charge unmapped even though the source gives a standard, quantifiable rate: a port-specific basic fee plus a fee per 100 tons or part thereof. That is a base-plus-tonnage pricing rule; the conditional 50% surcharge does not make the underlying charge unpriceable. The source’s surcharge conditions can be retained as modifiers rather than treating the whole charge as unmapped.
