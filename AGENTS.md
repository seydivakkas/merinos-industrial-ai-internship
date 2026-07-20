# AI Coding Agent Master Instructions

You are implementing one day of a 40-day Computer Engineering Industrial AI internship portfolio.

The repository follows a progressive engineering curriculum:

Environment/Data
→ Computer Vision
→ Deep Learning
→ Vector Search
→ Information Retrieval
→ RAG
→ Generative AI
→ API/MLOps
→ Release Engineering.

For the requested DAY XX:

CREATE EXACTLY THREE PRIMARY ARTIFACTS:

1. dayXX_<topic>.ipynb
2. README.md
3. mini_project/

---

## NOTEBOOK REQUIREMENTS

The notebook must teach and demonstrate the day's subject.

Use this structure:

1. Problem
2. Why the problem matters
3. Engineering concepts
4. Library/API investigation
5. Minimal implementation
6. Experiment
7. Visualization where relevant
8. Validation
9. Failure cases
10. Conclusions

Do not use notebook cells as the production implementation.
Reusable code must move into `mini_project/src/`.

---

## README REQUIREMENTS

Include:

# Day XX — Title
## Goal
## Engineer Research Assignment
## Concepts
## Libraries
## Functions / Classes Studied
## Notebook
## Mini Project
## Architecture
## Experiments
## Validation
## Results
## Limitations
## Files
## How to Run
## Next Day
## AI Coding Agent Prompt

---

## MINI PROJECT REQUIREMENTS

Structure:

mini_project/
├── README.md
├── src/
├── tests/
├── configs/
└── outputs/

Use:
- type hints
- pathlib
- logging
- deterministic seeds
- configuration instead of hard-coded values
- validation
- meaningful exceptions
- unit tests

---

## DATA POLICY

Never use:
- confidential Merinos data
- internal credentials
- customer information
- proprietary source code
- private documents

Use:
- synthetic data
- public data
- permissively licensed examples

---

## EXPERIMENT POLICY

Never fabricate:
- accuracy
- benchmark numbers
- latency
- GPU memory
- model output
- experiment results

If a test has not actually been executed write:

NOT_EXECUTED

instead of inventing a value.

---

## AI POLICY

Model output is not automatically ground truth.

For RAG:
evaluate retrieval and generation separately.

For generative images:
do not claim manufacturing feasibility, copyright safety or aesthetic quality based only on automated metrics.

For visual similarity:
do not equate embedding similarity with semantic identity.

---

## FOR EACH DAY FINISH WITH:

- files created
- tests executed
- test results
- experiments executed
- unresolved limitations
- suggested Git commit message

Keep each day's work technically defensible in a Computer Engineering internship interview.
