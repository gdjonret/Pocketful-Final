# Factory

## 1. Overview

This repository was produced using a three-seat autonomous software engineering factory running in BAND Desktop.

The factory is designed around a simple principle:

> **Planning, implementation, and acceptance should be separate responsibilities.**

A successful implementation is not accepted merely because it builds or passes an automated test suite. It must also survive independent review of the exact committed revision.

The factory consists of three persistent seats:

- **Planner** — coordinates the work and owns stage completion.
- **Implementer** — turns scoped requirements into committed, tested software.
- **Reviewer** — independently verifies the implementation and either accepts or rejects the exact revision.

The same factory structure can be used for software projects unrelated to Pocketful. Task-specific requirements belong in the task/specification supplied to the factory, not in the seat mandates.

## 2. Execution Configuration

| Configuration | Value |
|---|---|
| Platform | BAND Desktop |
| Harness | Codex |
| Model | GPT-5.6-Sol |
| Seats | Planner, Implementer, Reviewer |
| Result repository | Shared Git repository |
| Review model | Independent exact-revision review |
| Progression model | Sequential, cumulative stages |

Each seat has a corresponding generic mandate:

```text
mandates/planner.md
mandates/implementer.md
mandates/reviewer.md
```

The mandates describe how the seats work, communicate, own work, and reject or accept work. They intentionally do not encode Pocketful-specific endpoints, business rules, error codes, or implementation solutions.

## 3. Factory Architecture

```text
                         HUMAN
                           |
                    Stage specification
                           |
                           v
                       PLANNER
                           |
                 Complete scoped handoff
                           |
                           v
                     IMPLEMENTER
                           |
                    Committed revision
                           |
                           v
                      REVIEWER
                     /        \
                 ACCEPT      REJECT
                    |           |
                    |      Defect evidence
                    |           |
                    |           v
                    |      IMPLEMENTER
                    |           |
                    |     Corrected revision
                    |           |
                    |           v
                    +------ REVIEWER
                           |
                           v
                       PLANNER
                           |
                     Final report
```

The Reviewer is deliberately outside the implementation path. Its role is not to confirm the Implementer's conclusions, but to challenge them independently.

## 4. Seat Ownership

### Planner

The Planner owns orchestration. It interprets the supplied specification, breaks work into executable units, provides complete requirements in delegated handoffs, coordinates the Implementer and Reviewer, tracks accepted baselines, protects accepted work from unintended regression, requires correction when review identifies a blocker, waits for independent acceptance before closing a stage, and reports the final accepted revision and evidence.

The Planner does not treat an implementation report or passing harness as automatic acceptance.

### Implementer

The Implementer owns implementation. It implements scoped requirements, works from the complete specification supplied through the factory, preserves previously accepted behavior, creates verification assets where appropriate, builds and exercises the implementation, produces clean reviewable Git commits, reports the exact revision and evidence, and corrects independently reported defects without rewriting accepted history.

The Implementer does not approve its own work.

### Reviewer

The Reviewer owns independent acceptance. It reviews the exact committed revision, inspects the specification independently, examines affected behavior, runs relevant automated verification, performs adversarial and boundary testing, reproduces suspected defects, checks regression behavior, verifies corrections against the original failure, and returns either explicit acceptance or actionable blocking evidence.

A passing automated harness is evidence for the Reviewer, not a replacement for the Reviewer.

## 5. Generic Mandate Design

The mandates define **how the factory operates**, while the dispatched specification defines **what the factory builds**.

A reusable mandate may say:

> Reject a revision that does not satisfy the supplied specification.

A mandate should not encode task-specific requirements such as a particular endpoint, business rule, or error code.

This separation allows the same Planner, Implementer, Reviewer topology and mandates to be reused with a different application specification.

## 6. Human Boundary and Autonomous Execution

The human establishes the factory and supplies the stage specification. After dispatch, responsibility transfers to the factory for planning, delegation, implementation, testing, debugging, independent review, correction, re-review, and final reporting.

The submitted final room is the evidence source for the autonomous run.

Earlier BAND rooms were used during experimentation and preparation. They are not represented as the submitted autonomous execution. This distinction is also important when interpreting aggregate BAND usage statistics.

## 7. Stage Execution Protocol

Stages are executed sequentially:

```text
Stage 1 -> accepted baseline
        -> Stage 2 -> accepted baseline
        -> Stage 3 -> accepted baseline
        -> Stage 4
```

Each later stage inherits the requirements and behavior of previous accepted stages. The factory therefore treats a previous accepted stage as a protected baseline, not disposable scaffolding.

The same repository, room, seats, mandates, and workflow are maintained across the staged final run. Each new stage receives a separate dispatch so that stage boundaries remain explicit.

## 8. Handoff Protocol

Delegation is designed to be self-contained. A receiving seat receives enough information to perform its work without depending on vague references to earlier room discussion.

Important requirements, constraints, acceptance conditions, repository state, and revision information travel with the handoff. This reduces hidden context dependencies and makes responsibility boundaries observable in the room log.

## 9. Git and Revision Protocol

Git revisions are part of the factory's control mechanism:

1. Work reaches review as a committed revision.
2. The Reviewer evaluates a specific revision.
3. Acceptance applies to that exact revision.
4. A rejected revision is corrected with a new revision.
5. The correction is independently re-reviewed.
6. Accepted prior stages are protected from unintended changes.
7. History is preserved rather than rewritten to hide failed attempts.

The Git history and BAND room log complement each other as factory evidence.

## 10. Verification and Acceptance Gates

```text
Implementation
      |
      v
Local verification
      |
      v
Docker build/runtime verification
      |
      v
Official harness
      |
      v
Independent Reviewer
      |
      v
Adversarial/specification verification
      |
      v
Exact-revision acceptance
```

### Passing the Harness Is Not Acceptance

> **A passing automated harness is necessary evidence, but it is not by itself the factory's acceptance criterion.**

Automated verification can only exercise cases encoded in the tests. The Reviewer is expected to reason from the specification and probe behavior that automated checks may not cover.

The Pocketful run demonstrated why this distinction matters.

## 11. Failure and Recovery Protocol

When the Reviewer identifies a blocker:

```text
Reviewer finds blocker
        |
        v
REJECT exact revision
        |
        v
Report reproduction/evidence
        |
        v
Implementer creates correction
        |
        v
New committed revision
        |
        v
Reviewer reproduces original failure
        |
        v
Regression verification
        |
        v
ACCEPT or REJECT
```

The original failing revision remains visible in history. This makes recovery auditable and prevents a correction from being considered successful merely because the Implementer says it is fixed.

## 12. Pocketful Run Evidence

Pocketful served as the concrete workload used to exercise the factory.

| Stage | Final Outcome | Factory Evidence |
|---|---|---|
| Stage 1 | PASS | Established the initial implementation baseline |
| Stage 2 | PASS | Extended the baseline while preserving Stage 1 behavior |
| Stage 3 | PASS / Independently Accepted | Independent review found and forced correction of a historical-state defect |
| Stage 4 | PASS / Independently Accepted | Independent review found and forced correction of an import-integrity defect |

The final independent Stage 4 harness execution reported:

```text
Stage 1: PASS
Stage 2: PASS
Stage 3: PASS
Stage 4: PASS
Highest contiguous stage: 4
```

Final Stage 4 accepted revision:

```text
25709c2a68659a76c3af3a3837337faf8b11bcca
```

The stronger evidence is not merely reaching Stage 4. Independent review prevented two harness-passing advanced revisions from being accepted with undiscovered defects.

## 13. Failure Case Study — Stage 3

Initial candidate:

```text
3e9ec896...
```

The candidate passed the shipped automated harness. Independent review nevertheless discovered a cross-version historical-state defect: importing a captured authorization originating from Stage 2 state into Stage 3 lost the earlier authorization hold interval.

The Reviewer did not accept the harness-passing candidate.

The implementation was corrected to reconstruct missing lifecycle history from authorization creation and ordered linked captures while preserving native Stage 3 events.

Corrected and independently accepted revision:

```text
8d0e52a731b2cdcb527f629b5c31242593f4d616
```

The Reviewer independently reproduced the cross-version scenario and verified historical and current total, held, and available balances.

Final verification included:

```text
Lead official isolated run:
Stage 1 PASS
Stage 2 PASS
Stage 3 PASS

Independent Reviewer run:
Stage 1 PASS
Stage 2 PASS
Stage 3 PASS

verify.py: PASS
verify_stage2.py: PASS
verify_stage3.py: PASS
Fresh Docker builds: PASS
```

No blocking functional defect remained. One verification limitation was reported: host Go was unavailable to the Reviewer. Docker builds nevertheless compiled the service and the containerized/API verification suites passed.

## 14. Failure Case Study — Stage 4

Initial candidate:

```text
0def8e2...
```

The candidate passed the official Stage 1–4 harness. Independent review nevertheless discovered an import-integrity defect: a tampered exported state containing a refund whose `refund_of` referenced a nonexistent payment could be imported successfully.

The Reviewer rejected the candidate despite the green harness.

Corrected revision:

```text
25709c2a68659a76c3af3a3837337faf8b11bcca
```

The Reviewer independently reproduced the former blocker. After correction, the tampered dangling `refund_of` returned `422 validation_failed`. A subsequent export was JSON-value identical to the pre-attempt state, demonstrating atomic rejection, while a valid unchanged export continued to import successfully.

Independent verification included:

```text
stage-4/verify.py: PASS
verify_stage2.py: PASS
verify_stage3.py: PASS
verify_stage4.py: PASS
Fresh Stage 4 Docker build/start: PASS

Official isolated harness:
Stage 1 PASS
Stage 2 PASS
Stage 3 PASS
Stage 4 PASS
Highest contiguous stage: 4
```

The Reviewer explicitly accepted exact revision `25709c2a68659a76c3af3a3837337faf8b11bcca`. No remaining blocking defects or verification limitations were reported.

## 15. Why Independent Review Matters

Stages 3 and 4 demonstrate the reason the Reviewer exists as a separate seat.

In both cases:

```text
Implementation completed
        +
Official harness passed
        |
        v
Independent review
        |
        v
Previously undetected defect found
        |
        v
Candidate rejected
        |
        v
Correction committed
        |
        v
Original failure independently reproduced
        |
        v
Regression verification passed
        |
        v
Exact revision accepted
```

If the factory had treated a green automated harness as sufficient, both initial candidates could have been accepted. The Reviewer was therefore not a ceremonial approval step; it materially changed the delivered implementation.

## 16. Design Decisions and Tradeoffs

### Three Specialized Seats

Three seats provide clear ownership and separation of concerns while keeping coordination overhead manageable. The tradeoff is additional communication and model usage; the benefit is independent acceptance.

### Independent Reviewer

Separating review from implementation costs additional execution time and model capacity but reduces the risk of implementation assumptions propagating directly into acceptance. Stage 3 and Stage 4 demonstrated the value of this cost.

### Exact-Revision Acceptance

Review decisions are tied to Git revisions rather than descriptions such as "the latest version." This adds stricter coordination around commits but improves reproducibility and traceability.

### Preserved Git History

Corrections are represented as new revisions rather than rewriting failed attempts. This creates a stronger engineering evidence trail.

### Cumulative Stages

Later stages extend accepted earlier behavior. This increases regression risk, which is why prior-stage verification and immutability checks are part of later-stage review.

### Specification-Driven Review

The Reviewer reasons from the specification rather than treating supplied tests as the complete definition of correctness. This requires more reasoning and adversarial testing, but the Stage 3 and Stage 4 findings demonstrate why it is useful.

## 17. Measured Usage and Cost

BAND's agent analytics displayed the following aggregate measurements for the captured seven-day window:

| Seat | 7-Day Spend | Messages | Tool Calls | Errors |
|---|---:|---:|---:|---:|
| Planner | $27.08 | 699 | 234 | 2 |
| Implementer | $34.45 | 1,443 | 488 | 2 |
| Reviewer | $18.34 | 1,113 | 378 | 0 |
| **Total** | **$79.87** | **3,255** | **1,100** | **4** |

### Measurement Boundary

These figures are **not the isolated cost of the submitted Pocketful final room**.

The same agents were used across multiple BAND rooms during the seven-day period, including experimentation and preparation before the final submitted room. The analytics view captured an agent-level seven-day aggregate rather than an isolated final-room cost.

```text
Measured 7-day aggregate agent spend: $79.87
Measured final-room-only spend: not isolated by the captured analytics view
```

The aggregate figures are reported for transparency and are not presented as a precise Pocketful-Final-Run cost.

The four reported **Errors** are BAND agent/platform telemetry events from this aggregate seven-day measurement window. They should **not** be interpreted as four Pocketful application defects, nor as four errors isolated to the final submitted run. Application-level defects and their correction/re-review evidence are documented separately in the stage evidence and review history.

## 18. Operational Constraint — Model Capacity

The factory encountered a Codex usage-capacity limit at the transition between Stage 3 and Stage 4.

Importantly, this did **not** interrupt Stage 3 implementation, correction, or independent review. Stage 3 had already completed its correction and re-review cycle, and the Reviewer had explicitly accepted revision:

```text
8d0e52a731b2cdcb527f629b5c31242593f4d616
```

The Reviewer had independently verified the exact Git revision, confirmed a clean working tree, confirmed that Stages 1 and 2 remained unchanged from the accepted baseline, built the relevant stages, run the Stage 3 verification suites, run the official isolated harness through Stages 1–3, and independently reproduced the former cross-version historical-balance defect against the corrected implementation.

The usage limit occurred immediately afterward, when the Planner attempted to continue execution. BAND reported that the Codex usage limit had been reached.

Therefore, the interruption occurred **between an independently accepted Stage 3 result and Stage 4 execution**, rather than during Stage 3 correctness work.

The accepted repository state was already safely represented by Git revision:

```text
8d0e52a731b2cdcb527f629b5c31242593f4d616
```

When execution resumed, the human dispatched Stage 4 and explicitly identified that revision as the accepted Stage 3 baseline. The Planner then recognized the preserved state, closed the Stage 3 workflow, and began Stage 4 from the accepted revision.

No Stage 3 implementation or correction work needed to be reconstructed.

This exposed an important operational property:

> **Model capacity is a finite production resource, even when the software state itself is safely preserved.**

The interruption demonstrated that model-capacity planning matters not only during implementation and review, but also at stage boundaries.

Future runs should reserve sufficient model capacity for implementation, independent review, at least one correction/re-review cycle, final reporting, and transition into the following stage.

The repository and revision-based acceptance model made the interruption recoverable because the factory's accepted software state did not depend on an agent retaining conversational working memory.

## 19. Measured Stage Execution Time

Stage execution time was measured from the timestamp of the human stage dispatch to the final acceptance event recorded in the submitted BAND room.

These measurements represent **wall-clock factory duration**, not active model-compute time. They include planning, delegation, implementation, builds, automated verification, independent review, correction/re-review where applicable, and normal coordination overhead.

| Stage | Dispatch (UTC) | Acceptance endpoint | Wall-clock duration |
|---|---|---|---:|
| Stage 1 | 2026-10-05 04:10:27.602 | Planner final accepted Stage 1 report at 04:47:00.230 | **36m 32.6s** |
| Stage 2 | 2026-10-05 05:02:26.504 | Reviewer accepted `47e0b814...` at 05:48:45.948 | **46m 19.4s** |
| Stage 3 | 2026-10-05 06:11:07.414 | Reviewer accepted `8d0e52a...` at 06:58:50.676 | **47m 43.3s** |
| Stage 4 | 2026-10-05 07:35:31.674 | Reviewer accepted `25709c2...` at 07:58:49 | **23m 17.3s** |

### Interpretation

Stage 1 is measured to the Planner's final Stage 1 report because the room log records the stage as complete and independently accepted there. Stage 2, Stage 3, and Stage 4 use the Reviewer's exact-revision acceptance as the endpoint.

Stage 3's duration ends at the Reviewer's acceptance of `8d0e52a731b2cdcb527f629b5c31242593f4d616`. The later Codex usage-limit interruption is **not included in Stage 3 execution time**, because Stage 3 correctness work and independent acceptance were already complete.

The gap between Stage 3 acceptance and the Stage 4 dispatch is approximately **36 minutes 41 seconds**. This interval contains the Codex capacity interruption described in the previous section and is treated as a stage-transition delay rather than Stage 3 execution time.

The four stage durations sum to approximately **2 hours 33 minutes 53 seconds** of measured stage-level wall-clock execution. This sum intentionally excludes the gaps between separate human stage dispatches.

These timing measurements should not be converted directly into token usage or dollar cost. Model usage depends on the amount and type of reasoning, tool execution, retries, and context processed rather than elapsed time alone.

## 20. Lessons Learned

### A Green Harness Is Not Sufficient Evidence of Correctness

Stages 3 and 4 both contained defects discovered only during independent review after automated verification passed.

### Review Capacity Must Be Protected

Independent review consumes time and model resources. The Stage 3 capacity interruption showed that execution budgets should reserve resources for review and correction.

### Review Should Reproduce the Original Failure

A correction should not be accepted only because new tests pass. The Reviewer should rerun the scenario that originally caused rejection.

### Exact Revisions Improve Accountability

Exact-hash review eliminates ambiguity about what implementation received an acceptance decision.

### Cross-Version Behavior Deserves Adversarial Testing

Cumulative systems can fail at boundaries between accepted versions even when common paths appear correct. Stage 3 demonstrated this through imported Stage 2 authorization history.

### Failed Candidates Are Useful Evidence

A rejected revision is not necessarily a factory failure. If the factory detects the defect before acceptance, produces a correction, independently verifies it, and preserves the evidence trail, the rejection demonstrates that quality control worked.

## 21. Reproducing the Factory

A team can reproduce this factory by:

1. Creating three persistent seats: Planner, Implementer, and Reviewer.
2. Configuring each seat with `Harness: Codex` and `Model: GPT-5.6-Sol`.
3. Applying the corresponding generic mandate from `mandates/`.
4. Giving the seats access to the same result repository.
5. Placing the seats in the same BAND room.
6. Supplying the complete task specification to the Planner.
7. Having the Planner delegate complete scoped requirements to the Implementer.
8. Requiring implementation work to reach review as a committed revision.
9. Requiring the Reviewer to independently verify the exact revision.
10. Treating automated checks as evidence, not automatic acceptance.
11. Sending actionable evidence through the correction loop after rejection.
12. Requiring a new revision after correction.
13. Requiring independent re-review of the corrected revision.
14. Closing work only after the configured acceptance gate is satisfied.
15. Preserving the room export and Git history as evidence.

A different software specification can replace Pocketful without changing the factory topology or embedding that specification into the mandates.

## 22. Evidence Map

| Artifact | Purpose |
|---|---|
| `FACTORY.md` | Explains the factory design, operation, tradeoffs, and lessons |
| `mandates/planner.md` | Defines generic Planner behavior |
| `mandates/implementer.md` | Defines generic Implementer behavior |
| `mandates/reviewer.md` | Defines generic Reviewer behavior |
| `room.json` | Preserves actual agent communication and handoffs |
| Git history | Preserves revisions, corrections, and accepted baselines |
| `stage-*/` | Contains cumulative application implementations |
| `stage-*/RUN.md` | Describes how individual stages are run |
| Verification assets | Support reproducible application verification |

`FACTORY.md` explains the design. The mandates define reusable seat behavior. `room.json` and Git history demonstrate what actually happened.

## 23. Final Outcome

The factory completed the Pocketful workload through Stage 4.

The final independently accepted Stage 4 revision is:

```text
25709c2a68659a76c3af3a3837337faf8b11bcca
```

Independent verification of that revision reported:

```text
Stage 1 PASS
Stage 2 PASS
Stage 3 PASS
Stage 4 PASS
Highest contiguous stage: 4
```

No remaining Stage 4 blocking defects or verification limitations were reported.

More importantly, two advanced-stage candidates passed automated harness verification but were still rejected by independent review. Both defects were corrected, the original failure conditions were independently reproduced against the corrections, regression verification passed, and exact corrected revisions were accepted.

The resulting evidence supports the central factory principle:

> **Implementation produces a candidate. Independent verification earns acceptance.**
