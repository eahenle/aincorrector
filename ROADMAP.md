# Implementation Roadmap (Next Slate)

This roadmap turns the PRD into an execution queue with clear blockers first.

## 1) Critical Path (do next)

1. **Backend abstraction hardening**
   - Finalize an adapter interface for OpenAI-compatible and local vLLM backends.
   - Add contract tests to ensure consistent behavior across backends.
2. **Latency instrumentation pass**
   - Add per-stage timings to logs for: authentic prefix, mutation, first-token latency, total stream.
   - Add threshold assertions in tests for synthetic timing fixtures.
3. **Mutation quality harness**
   - Add a reproducible evaluation script for rating fluency/wrongness/confidence/seamlessness.
   - Produce aggregate score output for quick regressions.

## 2) Near-Term Enhancements

4. **Wrongness mode expansion**
   - Implement remaining style presets from PRD with prompt templates and tests.
5. **Prefix candidate search (beam-lite)**
   - Generate N mutated prefixes and score with a lightweight plausibility heuristic.
6. **Replay UX improvements**
   - Add filters/grouping in replay output by domain and style.

## 3) Safety Boundaries for Experimental Use

7. **Domain guard policy refinement**
   - Expand sensitive-domain patterns and add explicit audit logs for blocked requests.
8. **Comedy-only safeguards**
   - Enforce a guardrail mode that rejects non-sandbox usage contexts.

## 4) Release Readiness Checklist

9. **CLI polish**
   - Improve help text, examples, and error messaging.
10. **Docs and examples**
    - Add end-to-end examples and expected logs for each style.
11. **CI quality gates**
    - Ensure linting, typing, formatting, and tests run in CI with clear failure triage.

---

## Definition of Done (for each item)

- Feature has unit tests and (where applicable) integration tests.
- Logging includes enough context for replay and debugging.
- CLI behavior is documented in README/usage docs.
- No regressions in existing test suite.
