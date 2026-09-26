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

## DATA & SYSTEM REALITY POLICY (PERMANENT AGENT CONTRACT)

1. **No Proprietary / Confidential Data:**
   - Never use confidential Merinos data, internal credentials, customer information, proprietary source code, or private documents.
   - Use exclusively: synthetic data, public domain data, permissively licensed examples.

2. **No False Production or Live Claims:**
   - Never write as if live SCADA/PLC, live production sensors, real loom telemetry, physical factory cameras, or internal production systems were directly connected.
   - All implementations are local learning prototypes / Proof-of-Concept (PoC), not live industrial production deployments.
   - Future architectural possibilities must be explicitly labeled as "Gelecekteki Entegrasyon Senaryosu / Future Work", never as already deployed.

3. **Standalone Notebook Principle:**
   - Every `dayXX/*.ipynb` notebook must run 100% standalone without external file dependencies, missing disk assets, or private package imports. Anyone opening the notebook must be able to execute "Run All" cleanly.

4. **Curriculum Alignment & Boundary Isolation:**
   - Each `dayXX` must strictly adhere to its official curriculum topic as defined in `ROADMAP.md` and the 80-page staj defteri.
   - Reusable code belongs in `mini_project/src/`. Code belonging to other days must not be deleted, but moved using `git mv` to its proper day.
   - The official staj defteri (`Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md`) is the master document and MUST NEVER BE MODIFIED.

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
