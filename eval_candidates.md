## Day 3 observations

- Test PR: MPatel2110/ai-pr-reviewer#1 (test_sample.py with planted divide-by-zero + SQL injection)
- Comments returned: 3
  - ✓ Divide-by-zero correctly flagged as ERROR/bug at L2
  - ✓ SQL injection correctly flagged as CRITICAL/security at L6
  - ⚠ Missing trailing newline flagged as INFO/style at L7 — accurate but low-value nitpick. Consider suppressing in prompt on Day 4.

## Behaviors to test

- [ ] Clean diff (no issues) — should return empty
- [ ] Large multi-file PR — does cost stay reasonable?
- [ ] PR with only docs changes — what does it say?
- [ ] PR with mixed Python + lockfile — filter should drop lockfile
