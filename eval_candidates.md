## Day 3 observations

- Test PR: MPatel2110/ai-pr-reviewer#1 (test_sample.py with planted divide-by-zero + SQL injection)
- Comments returned: 3
  - ✓ Divide-by-zero correctly flagged as ERROR/bug at L2
  - ✓ SQL injection correctly flagged as CRITICAL/security at L6
  - ⚠ Missing trailing newline flagged as INFO/style at L7 — accurate but low-value nitpick. Consider suppressing in prompt on Day 4.

## Day 4 context-aware review — PR test

Test: MPatel2110/marvel-rivals-tracker#1 — added refresh_player_route to app.py
Planted bugs: (a) unhandled APIError on get_player, (b) wrong arg count to db.save_player

**No-context run:**

- ✓ Caught unhandled APIError (L83)
- ✗ Missed save_player signature mismatch
- ⚠ Flagged hypothetical KeyError on player_data["username"] (L84) — known prompt weakness

**With-context run:**

- ✗ Missed unhandled APIError
- ✗ Missed save_player signature mismatch (the one we hoped context would catch)
- ⚠ Flagged same hypothetical KeyError (L83)

Finding: context-aware infrastructure works (clone, AST parsing, prompt injection all functional)
but adding context made review quality WORSE on this PR, not better.

Hypotheses:

- Context section may dilute model attention away from the diff
- Prompt doesn't explicitly instruct cross-referencing call sites against signatures in context
- "do NOT review these" framing on context may be interpreted as "ignore these"

Decision: ship the basic context infrastructure as v1, time-box prompt iteration.
Day 5+ will revisit with more PRs (N>1) and explicit cross-reference instructions if needed.

Resume bullet implication: feature can be honestly described as "context-aware reviews
pulling related project files." It works mechanically. Quality lift requires more eval data.

## Day 4 prompt caching — explicit vs implicit

Attempted explicit cache via client.caches.create() with system_instruction.
API returned 400: cached content too small (849 tokens, min 1024 for gemini-2.5-flash).

Decision: use implicit caching instead.

- Gemini auto-caches repeated prompt prefixes server-side
- ~25% discount vs explicit's ~75%, but no minimum-size constraint
- Triggered automatically by reusing system_instruction across requests
- Zero additional code

Interview talking point: evaluated both approaches, chose implicit for workload fit.
Padding the system prompt to clear the threshold was considered and rejected as
anti-pattern (longer prompts for no quality benefit).
