# Pocketful — BAND Dark Factory Hackathon

This repository is the final **Pocketful** submission for the BAND AI Dark
Factory / WeAreDevelopers Hackathon.

It contains the incremental Pocketful implementation produced by our
multi-agent software factory, the generic mandates that define how the factory
operates, and the BAND room export containing the collaboration evidence from
the submitted run.

## Team

- **Eric Muhirwa Kalisa**
- **Gloria Djonret**

## Track

**Pocketful**

Official challenge repository:

https://github.com/band-ai/dark-factory-wearedevs

## What Is Pocketful?

Pocketful is a wallet and payment service developed incrementally across four
dependent stages.

The application supports wallet-to-wallet payments, payment requests, bill
splitting, activity, settlements, authorizations and captures, payment
corrections, historical accounting, refunds, and atomic correction batches.

The browser product exposes the interactive wallet flows, while additional
stage-specific behavior is available through the HTTP API as required by the
Pocketful specification.

## Final Result

The factory completed all four Pocketful stages.

| Stage | Main Scope | Result |
| --- | --- | --- |
| Stage 1 | Payments, requests, splits, activity, and settlements | PASS |
| Stage 2 | Browser product, authorizations, holds, and captures | PASS |
| Stage 3 | Payment corrections and historical/temporal accounting | PASS |
| Stage 4 | Refunds and atomic correction batches | PASS |

Final isolated verification reached:

```text
Stage 1: PASS
Stage 2: PASS
Stage 3: PASS
Stage 4: PASS

Highest contiguous stage: 4