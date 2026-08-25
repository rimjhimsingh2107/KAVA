# KAVA

AI-powered insurance claim validation with tamper-proof scoring.

## Overview

Insurance claims are scored slowly and inconsistently, and the reasoning
behind a decision is rarely something the claimant can inspect. KAVA scores a
claim against a weighted rulebook, shows every deduction, and runs the
evaluation inside a trusted execution environment so the result cannot be
quietly altered afterwards.

Claims are submitted through a wizard with photos and receipts. Claude Vision
assesses damage from the images, and the rule engine produces a rule-by-rule
breakdown rather than a single opaque number — including which documents are
missing and what each would be worth to the score.

## How a claim is scored

Every claim is evaluated against a fixed rulebook, so two identical claims
score identically. The score is a weighted combination of three categories:

| Category | Weight | Checks |
|:--|--:|:--|
| Completeness | 45% | Before/after property photos, receipts for items over $100, expenses inside the coverage period, valid policy documentation |
| Damage assessment | 28% | Direct wildfire causation, replacement costs against market rate, timeline consistency |
| Documentation quality | 27% | Photo clarity and context, receipt legibility, authenticity markers |

Each rule returns its own confidence rather than a boolean, and those combine
into the overall score. A claim needs 70% or above to clear for automatic
approval; below that it routes to a human with the specific failing rules
attached.

Running in parallel, fraud detection looks for signals that individual rules
miss on their own — amount anomalies against comparable claims, timing
inconsistencies between the incident and the filing, and patterns of missing
evidence that tend to appear together.

Because a score is only worth as much as its auditability, each evaluation is
attested in a TEE and anchored on chain as a proof card holding the claim hash
(SHA-256), the agent signature, the validation timestamp, the score, and the
version of the rulebook that produced it. Re-running an old claim against a
newer rulebook is therefore detectable rather than silent.

## Tech Stack

Frontend

- Next.js
- React
- Tailwind CSS

Backend

- FastAPI
- Python

AI

- Claude Vision for document and damage analysis

Verification

- EigenCloud TEE
- Solidity
