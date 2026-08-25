# KAVA

AI-powered insurance claim validation with tamper-proof scoring.

## Overview

Insurance claims are scored slowly and inconsistently, and the reasoning
behind a decision is rarely something the claimant can inspect. KAVA scores a
claim against a weighted set of rules, shows every deduction, and runs the
evaluation inside a trusted execution environment so the result cannot be
quietly altered afterwards.

Claims are submitted through a wizard with photos and receipts. Claude Vision
assesses damage from the images, and the rule engine scores completeness,
damage severity, documentation quality and fraud indicators. The output is a
rule-by-rule breakdown rather than a single opaque number, including which
documents are missing and what each would be worth to the score.

Validation

- Weighted scoring across completeness, damage, documentation and fraud
- Computer-vision damage assessment from claim photos
- Fraud signals: amount anomalies, timing inconsistencies, missing evidence
- Missing-document detection with specific next steps

Verification

- Evaluations attested inside an EigenCloud TEE
- On-chain proof record for each decision

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
