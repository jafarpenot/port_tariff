# Extraction run — 2026-09-29T03:57:20+00:00

**PDF:** /Users/jafarpenot/Desktop/my_projs/port_tariff/Port Tariff.pdf
**Model:** gpt-6-luna
**Thread ID:** fullcompare-classical-tnpa

Written live as the run progresses, not just at the end — if this file stops mid-trace with no "Final report" section below, the run crashed or is still in progress; everything above the cutoff genuinely happened.

## Live trace
```
structure_scan: 2748 chars
identity: authority='Transnet National Ports Authority' currency='ZAR'
map: 9 windows, 148 sections found
assemble: 13 out-of-scope sections, general_terms_found=True
light_dues: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19] sections=['6', '1.1', '1.1.1']
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: validate -> valid
light_dues: verify -> material finding
light_dues: done
port_dues: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] sections=['6', '4', '4.1', '4.3', '4.1.1', '4.1.2', '4.2']
port_dues: validate -> valid
port_dues: verify -> material finding
port_dues: validate -> valid
port_dues: verify -> clean
port_dues: done
towage: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] sections=['6', '3', '3.1', '3.2', '3.3', '3.6', '3.7', '3.9', '4.8', '4', '4.1', '4.3']
towage: validate -> invalid
towage: validate -> valid
towage: verify -> material finding
towage: validate -> invalid
towage: validate -> invalid
towage: validate -> invalid
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
berthing_services: starting, context pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19] sections=['6', '3', '3.1', '3.2', '3.8', '3.9']
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: validate -> valid
berthing_services: verify -> material finding
berthing_services: done
```


## Final report — duration 1676.5s

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
#### light_dues — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
  - attempt 2: valid
    - (warning) value -100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- pricing_type: 'keyed_rate' params: {'key_dimension': 'vessel category', 'keys': [{'key': 'All other vessels', 'flat_amount': None, 'rate': 117.08}]}
- warning: value -100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- (material) The mapped gross-tonnage rate is represented as per-call, but the source says the 117.08 tariff applies per 100 tons or part thereof; it does not state that this base charge is simply per call. Applicability is tied to the first South African port call and its validity conditions, with a separate monthly basis after 60 days and special monthly treatment for bonafide coasters.

#### port_dues — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) value 192.73 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value 57.79 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) value -35.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
- (minor) The proposal cites pages 21–25 for Sections 4.1.1, 4.1.2, and 4.2, but the supplied text for pages 21–25 is Sections 7–8 on cargo dues and cargo documentation, not port dues. The port-dues snippets are identified as page 11, so the cited page range does not support the proposal.

#### towage — outcome=mapped status=extraction_failed
repair_attempts=3 verify_rounds=1
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
    - (warning) [Richards Bay] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 8050.76 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
  - attempt 3: invalid
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [East London] the final band's max_inclusive must be null (open-ended).
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Mossel Bay] the final band's max_inclusive must be null (open-ended).
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 4: invalid
    - (hard) [Richards Bay] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Richards Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Durban] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [East London] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (warning) [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Port Elizabeth / Ngqura] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth / Ngqura] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Mossel Bay] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (warning) [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Cape Town] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (hard) [Saldanha] smoke calculation raised TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 50.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 100.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha] value 25.0 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
- (material) The proposal extends East London's 50,001–100,000 GT rate band (25.80 per additional 100 GT or part thereof) above 100,000 GT. The source prints “n/a” for East London above 100,000 GT, so the proposal would assess a charge where this table gives no rate.
- (material) The proposal omits the marine-services incentive discount for craft assistance. The source says the incentive applies to craft assistance service charges, for eligible cargo-working vessels, with discounts determined by shipping-line call thresholds; this can reduce the towage charge.
- (material) The proposal does not preserve the source's incremental charging unit: additions are charged per 100 tons or part thereof above each threshold. It records the values as per_unit_rate without capturing that 100-ton-or-part unit, which changes the calculation if interpreted as a per-GT rate.
- (material) The Saldanha late-arrival/departure fee is stated as 10,152.19 per tug per half hour or part thereof, but the proposal records 10,152.20 (10,152.2).
- (material) The proposal omits the craft-allocation table: the source sets maximum craft numbers by vessel tonnage (0.50, 1, 2, 3, or 4) and says the port decides the craft type and number allocated. That allocation can change the number of towage services charged.

#### vts — outcome=mapped status=-
repair_attempts=0 verify_rounds=1
- validation history:
  - attempt 1: valid
    - (warning) [Richards Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [East London] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Ngqura] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Port Elizabeth] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Mossel Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Cape Town] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
  - attempt 2: valid
    - (warning) [All ports excluding Durban and Saldanha Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Durban] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
    - (warning) [Saldanha Bay] value 0.65 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
- per_port_rules: [('All ports excluding Durban and Saldanha Bay', 'per_unit', {'rate': 0.54}), ('Durban', 'per_unit', {'rate': 0.65}), ('Saldanha Bay', 'per_unit', {'rate': 0.65})]
- warning: [All ports excluding Durban and Saldanha Bay] value 0.54 not found verbatim on its cited page(s) — PDF formatting may differ from the raw number.
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
- (material) The incremental rate is specified as a charge per 100 tons or part thereof, not per gross ton. The proposal records the basis as gross_tonnage with rates such as 10.93 and 9.72 but omits the printed per-100-ton unit/rounding rule; applying the rate per GT would materially overcharge. The pilotage table labels the row “Per 100 tons or part thereof.”
- (material) The proposal lists both the general 30-minute cancellation surcharge and a separate Durban 60-minute cancellation surcharge, but does not state how the overlapping Durban conditions interact. The source prints a 50% surcharge for cancellation within 30 minutes at all ports and a Durban-specific 50% surcharge within 60 minutes; the proposal must not imply two cumulative 50% surcharges for Durban cancellations within 30 minutes unless the source establishes that they stack.

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
- (material) The base rates are printed as a fee per service plus an increment “per 100 tons or part thereof” (page 18). The proposal records only a gross-tonnage basis and rate, without representing the 100-ton increment and rounding up any partial 100-ton block; applying the rate per ton or proportionally would produce a different charge.
- (material) The page states that tariffs are subject to VAT at 15%, but the proposal omits this tax condition. The charged amount therefore is understated if the extracted tariff is treated as the full amount payable.
- (material) The tanker berthing-staff fee is a separate rate of 1,267.83 per hour or part thereof, limited to tanker vessels discharging crude/petroleum products at Mossel Bay and Saldanha. The proposal places it among modifiers rather than expressing the separate hourly charge, so its amount and hourly billing basis are not represented as a charge rule.

### Disagreements
- **light_dues**: The mapped gross-tonnage rate is represented as per-call, but the source says the 117.08 tariff applies per 100 tons or part thereof; it does not state that this base charge is simply per call. Applicability is tied to the first South African port call and its validity conditions, with a separate monthly basis after 60 days and special monthly treatment for bonafide coasters.
- **pilotage**: The incremental rate is specified as a charge per 100 tons or part thereof, not per gross ton. The proposal records the basis as gross_tonnage with rates such as 10.93 and 9.72 but omits the printed per-100-ton unit/rounding rule; applying the rate per GT would materially overcharge. The pilotage table labels the row “Per 100 tons or part thereof.”; The proposal lists both the general 30-minute cancellation surcharge and a separate Durban 60-minute cancellation surcharge, but does not state how the overlapping Durban conditions interact. The source prints a 50% surcharge for cancellation within 30 minutes at all ports and a Durban-specific 50% surcharge within 60 minutes; the proposal must not imply two cumulative 50% surcharges for Durban cancellations within 30 minutes unless the source establishes that they stack.
- **berthing_services**: The base rates are printed as a fee per service plus an increment “per 100 tons or part thereof” (page 18). The proposal records only a gross-tonnage basis and rate, without representing the 100-ton increment and rounding up any partial 100-ton block; applying the rate per ton or proportionally would produce a different charge.; The page states that tariffs are subject to VAT at 15%, but the proposal omits this tax condition. The charged amount therefore is understated if the extracted tariff is treated as the full amount payable.; The tanker berthing-staff fee is a separate rate of 1,267.83 per hour or part thereof, limited to tanker vessels discharging crude/petroleum products at Mossel Bay and Saldanha. The proposal places it among modifiers rather than expressing the separate hourly charge, so its amount and hourly billing basis are not represented as a charge rule.
