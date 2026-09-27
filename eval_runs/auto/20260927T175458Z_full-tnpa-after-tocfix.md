# Extraction run — 2026-09-27T17:54:58+00:00

**PDF:** Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** full-tnpa-after-tocfix

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
structure_scan: 2313 chars
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 9 windows, 132 sections found
assemble: 24 out-of-scope sections, general_terms_found=True
light_dues: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19] sections=['6', '1']
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: SYSTEM_ERROR — ValidationError: 1 validation error for ChargeExtraction
proposed_rule.modifiers.1
  Value error, exactly one of adjustment_percentage, adjustment_flat_amount, raw_description must be set [type=value_error, input_value={'condition': 'Qualifying... any similar facility.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
light_dues: done
port_dues: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26, 27] sections=['6', '4.1', '4.1.1', '4.2', '4.1.2', '8.3', '8', '8.1', '8.1.1', '8.1.1.1', '8.1.2', '8.3.1', '8.3.2', '8.4']
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: done
towage: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] sections=['6', '3.1', '3.2', '3.6', '3.7', '3.9', '4.8', '4.1']
towage: validate -> invalid
towage: validate -> valid
towage: verify -> material finding
towage: validate -> invalid
towage: validate -> invalid
towage: validate -> invalid
towage: done
vts: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19] sections=['6', '2']
vts: validate -> valid
vts: verify -> clean
vts: done
pilotage: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18, 19] sections=['6', '3.1', '3.2', '3.3', '3.5']
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: validate -> valid
pilotage: verify -> material finding
pilotage: done
berthing_services: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19] sections=['6', '3.1', '3.2', '3.8', '3.9']
berthing_services: validate -> valid
berthing_services: verify -> clean
berthing_services: done
```


## Final report — duration 1506.7s

### Identity
```
{'authority': 'Transnet National Ports Authority', 'jurisdiction': 'South African ports', 'ports': [], 'schedule_name': 'Port Tariffs', 'effective_from': '1 April 2024', 'effective_to': '31 March 2025', 'currency': 'ZAR'}
```
is_new_edition=True matched_existing_authority=Transnet National Ports Authority

### Coverage
- pages_read: 27/27
- general_terms_found: True
- out_of_scope_sections: 24

### Charges
#### light_dues — outcome=? status=system_error
repair_attempts=0 verify_rounds=0

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
- pricing_type: 'base_plus_increment_times_duration' params: {'basic_rate': 192.73, 'daily_rate': 57.79}
- warning: value 192.73 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value 57.79 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -35.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value 20.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -60.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -10.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: value -15.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The proposal states the 35% reduction for vessels not engaged in cargo working without the source's limitation that this reduction applies only for the first 30 days. The source separately lists bona fide coasters, passenger vessels, and qualifying small vessels, but the 30-day qualifier specifically appears in the non-cargo-working bullet; do not apply the 35% reduction to that category beyond the first 30 days.

#### towage — outcome=mapped status=extraction_failed
repair_attempts=3 verify_rounds=1
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
  - attempt 4: invalid
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
    - (hard) [East London] smoke calculation raised RateNotPublished: no rate published for GT 120000.0 at this port — the source prints n/a for this band
    - (warning) [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Mossel Bay] smoke calculation raised RateNotPublished: no rate published for GT 120000.0 at this port — the source prints n/a for this band
    - (warning) [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
  - attempt 5: invalid
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
- per_port_rules: [('Richards Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7001.67, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 13020.67, 'increment_above': 2000.0, 'per_unit_rate': 275.32}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 39999.88, 'increment_above': 10000.0, 'per_unit_rate': 101.08}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 79999.76, 'increment_above': 50000.0, 'per_unit_rate': 30.11}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 103999.7, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Durban', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 8140.0, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 12633.99, 'increment_above': 2000.0, 'per_unit_rate': 268.99}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 38494.51, 'increment_above': 10000.0, 'per_unit_rate': 84.95}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 73118.07, 'increment_above': 50000.0, 'per_unit_rate': 32.24}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 93548.13, 'increment_above': 100000.0, 'per_unit_rate': 23.65}]}), ('East London', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5622.16, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 200.97}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27956.91, 'increment_above': 10000.0, 'per_unit_rate': 66.67}]}), ('Port Elizabeth / Ngqura', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 7206.98, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 11168.45, 'increment_above': 2000.0, 'per_unit_rate': 237.53}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 32257.98, 'increment_above': 10000.0, 'per_unit_rate': 73.1}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 64515.95, 'increment_above': 50000.0, 'per_unit_rate': 21.5}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 82542.46, 'increment_above': 100000.0, 'per_unit_rate': 21.5}]}), ('Mossel Bay', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 6316.53, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 8152.14, 'increment_above': 2000.0, 'per_unit_rate': 173.37}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 25806.37, 'increment_above': 10000.0, 'per_unit_rate': 60.21}]}), ('Cape Town', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 5411.47, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 7898.57, 'increment_above': 2000.0, 'per_unit_rate': 194.63}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 27741.85, 'increment_above': 10000.0, 'per_unit_rate': 64.52}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 53978.33, 'increment_above': 50000.0, 'per_unit_rate': 47.32}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 79569.67, 'increment_above': 100000.0, 'per_unit_rate': 38.71}]}), ('Saldanha', 'banded', {'bands': [{'min_exclusive': 0.0, 'max_inclusive': 2000.0, 'base': 9038.42, 'increment_above': None, 'per_unit_rate': None}, {'min_exclusive': 2000.0, 'max_inclusive': 10000.0, 'base': 15378.78, 'increment_above': 2000.0, 'per_unit_rate': 327.43}, {'min_exclusive': 10000.0, 'max_inclusive': 50000.0, 'base': 47311.7, 'increment_above': 10000.0, 'per_unit_rate': 103.23}, {'min_exclusive': 50000.0, 'max_inclusive': 100000.0, 'base': 90322.33, 'increment_above': 50000.0, 'per_unit_rate': 27.97}, {'min_exclusive': 100000.0, 'max_inclusive': None, 'base': 111827.63, 'increment_above': 100000.0, 'per_unit_rate': 47.32}]})]
- warning: [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 10152.19 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) Richards Bay's rate above 100,000 tons is 23.65 per 100 tons or part thereof, not 21.50 as proposed.
- (material) Durban has no (n/a) incremental rate above 100,000 tons; the proposal instead applies 23.65 per 100 tons above that threshold.
- (material) East London has separate bands for 10,000–50,000 tons (base 27,956.91 plus 66.67 per additional 100 tons), 50,001–100,000 tons (base 55,913.82 plus 25.80), and above 100,000 tons (n/a). The proposal collapses these into one band above 10,000 at 66.67, changing charges above 50,000 tons and applying a rate where the source says n/a above 100,000.
- (material) Port Elizabeth/Ngqura's rate above 100,000 tons is n/a, not 21.50 per 100 tons as proposed; the printed 21.50 rate applies to the 50,001–100,000 band.

#### vts — outcome=mapped status=-
repair_attempts=0 verify_rounds=0
- per_port_rules: [('all ports excluding Durban and Saldanha Bay', 'per_unit', {'rate': 0.54}), ('Durban and Saldanha Bay', 'per_unit', {'rate': 0.65})]
- warning: [all ports excluding Durban and Saldanha Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Durban and Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.

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
    - (warning) [Other] value 6547.45 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Other] value 10.49 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
- (material) The mapped rates omit the 15% VAT stated as applying to the tariff. Unless VAT is applied downstream, the charged amount would be understated by 15%; include the VAT treatment or explicitly identify these figures as pre-VAT rates.

#### berthing_services — outcome=mapped status=-
repair_attempts=0 verify_rounds=0
- per_port_rules: [('Richards Bay', 'base_plus_increment', {'base': 3175.89, 'rate': 13.46}), ('Port Elizabeth / Ngqura', 'base_plus_increment', {'base': 3838.62, 'rate': 18.72}), ('Cape Town', 'base_plus_increment', {'base': 3052.33, 'rate': 14.92}), ('Saldanha', 'base_plus_increment', {'base': 4006.34, 'rate': 16.97}), ('Other Ports', 'base_plus_increment', {'base': 2801.91, 'rate': 13.68})]
- warning: [Richards Bay] value 3175.89 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 13.46 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 3838.62 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 18.72 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 3052.33 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 14.92 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 4006.34 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 16.97 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other Ports] value 2801.91 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other Ports] value 13.68 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- warning: [Other Ports] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.

### Disagreements
- **port_dues**: The proposal states the 35% reduction for vessels not engaged in cargo working without the source's limitation that this reduction applies only for the first 30 days. The source separately lists bona fide coasters, passenger vessels, and qualifying small vessels, but the 30-day qualifier specifically appears in the non-cargo-working bullet; do not apply the 35% reduction to that category beyond the first 30 days.
- **pilotage**: The mapped rates omit the 15% VAT stated as applying to the tariff. Unless VAT is applied downstream, the charged amount would be understated by 15%; include the VAT treatment or explicitly identify these figures as pre-VAT rates.
