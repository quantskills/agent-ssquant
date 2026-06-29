# Report Debugging

## Fixed Template Check

When the user asks whether reports use a fixed template:

1. Locate report export code.
2. Locate the generated HTML/Markdown path.
3. Generate two reports from different strategies.
4. Compare section order and required fields.
5. Treat missing charts, missing benchmark labels, or inconsistent field names as bugs.

## Common Bugs

- report generated but browser points to an old file
- strategy core printed metrics but HTML generator did not receive them
- charts missing because JS/CSS assets were not embedded or linked
- benchmark unclear or hardcoded
- same-day signal and same-day execution not disclosed
- rollover cost included in totals but missing from detail table
- futures account semantics accidentally reused in an unsupported asset class

## Benchmark Rule

Always identify the benchmark:

- name
- source
- date alignment
- adjustment
- whether it is price return or total return

If no benchmark is used, say so directly.
