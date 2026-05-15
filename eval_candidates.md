## Day 3 observations

- Test PR: MPatel2110/ai-pr-reviewer#1 (test_sample.py with planted divide-by-zero + SQL injection)
- Comments returned: 3
  - ✓ Divide-by-zero correctly flagged as ERROR/bug at L2
  - ✓ SQL injection correctly flagged as CRITICAL/security at L6
  - ⚠ Missing trailing newline flagged as INFO/style at L7 — accurate but low-value nitpick. Consider suppressing in prompt on Day 4.

## Day 4 v3 prompt — final fixture results

- 01 clean: ✓ empty
- 02 divide-by-zero: ✓ 1 ERROR/bug
- 03 SQL injection: ✓ 1 CRITICAL/security
- 04 unhandled file: ✓ 2 robustness comments (path-injection hallucination removed)
- 05 style only: ⚠ KeyError hypothetical persists despite negative example in prompt
  - Hypothesis: model's defensive-programming prior is strong; few-shot insufficient
  - Likely improves once context-aware review can see callers
  - Acceptable for v3. Revisit after context layer if needed.
