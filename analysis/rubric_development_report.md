# Error Collection Analysis & Rubric Development Report

## Overview

This report documents the qualitative rubric development process for classifying model errors in the AP Research Project. The rubric was developed through **open coding** of 80 stratified errors, followed by iterative refinement and testing.

---

## Phase 1: Error Collection Creation

### Sampling Method
- **Source:** 2,800 scored model responses across 3 result files (P1, P2, P3)
- **Total errors identified:** 2,023 (72.2% error rate)
- **Sample size:** 80 errors
- **Sampling method:** Stratified by model_group × problem_type

### Error Distribution (Full Collection)
| Model Group | Errors | Sampled |
|-------------|--------|---------|
| RLHF | 990 | 33 (41.2%) |
| non-RLHF | 1,033 | 47 (58.8%) |

### Sampled Error Distribution by Problem Type
| Problem Type | Count | Problem Type | Count |
|--------------|-------|--------------|-------|
| hle_math | 22 | mmlu_college_mathematics | 2 |
| hle_chemistry | 6 | mmlu_college_medicine | 2 |
| hle_physics | 5 | mmlu_college_physics | 2 |
| mmlu_miscellaneous | 5 | mmlu_conceptual_physics | 2 |
| mmlu_professional_medicine | 4 | mmlu_electrical_engineering | 2 |
| hle_engineering | 2 | mmlu_formal_logic | 2 |
| mmlu_abstract_algebra | 2 | mmlu_logical_fallacies | 2 |
| mmlu_anatomy | 2 | mmlu_machine_learning | 2 |
| mmlu_astronomy | 2 | mmlu_medical_genetics | 2 |
| mmlu_clinical_knowledge | 2 | mmlu_nutrition | 2 |
| mmlu_college_biology | 2 | mmlu_virology | 2 |
| mmlu_college_chemistry | 2 | | |

---

## Phase 2: Open Coding Process

### Methodology
1. **Read-through:** Systematically read all 80 errors without pre-set categories
2. **Pattern noting:** Documented recurring error patterns and anomalies
3. **Category emergence:** Allowed categories to emerge inductively from data
4. **Initial taxonomy:** Drafted initial error categories based on observed patterns

### Key Observations from Open Coding

#### Observed Pattern 1: Reasoning Quality ≠ Correctness
Many errors featured elaborate, well-structured reasoning that was completely incorrect. This pattern was particularly common in RLHF models.

**Example (E005):** 18+ lines of systematic option elimination, confidently concluding with wrong answer.

#### Observed Pattern 2: Self-Correction to Wrong Answers
Models would often start with correct reasoning, then "talk themselves into" incorrect conclusions through excessive qualification.

**Example (E019):** Correctly identifies 35 is divisible by 7, then selects 28 (not divisible by 7).

#### Observed Pattern 3: Hallucinated Domain Knowledge
Models frequently invented facts about molecules, equations, or concepts not present in the problem.

**Example (E002):** Claims SMILES string represents "acyl chloride" when it's actually a diene.

#### Observed Pattern 4: Simple Errors Within Complex Reasoning
Some errors were basic calculation or logic mistakes embedded in otherwise sound approaches.

**Example (E021):** "79.0 eV / 2 = 39.5 eV" - simple arithmetic but invalid physical reasoning.

---

## Phase 3: Category Development

### Initial Categories (from open coding)
1. **Logic Errors** - Invalid deductions, contradictions
2. **Knowledge Errors** - Wrong facts, hallucinations
3. **Method Errors** - Wrong approaches, missing steps
4. **Calculation Errors** - Arithmetic mistakes
5. **Understanding Errors** - Problem misreading
6. **Output Errors** - Format mismatches
7. **Alignment Patterns** - RLHF-associated behaviors

### Refined Categories (after testing)

| Category | Subtypes | Description |
|----------|----------|-------------|
| **LOGIC** | L1-L4 | Invalid deductions, contradictions, circular reasoning |
| **FACTUAL** | F1-F4 | Hallucinations, incorrect facts, concept misapplication |
| **PROCEDURAL** | P1-P4 | Missing steps, wrong methods, constraint loss |
| **CALCULATION** | C1-C4 | Arithmetic, algebraic, unit, sign errors |
| **COMPREHENSION** | M1-M4 | Misread questions, option confusion, symbol errors |
| **RLHF_PATTERN** | R1-R5 | Persuasive incorrect, hedging, sycophancy, verbose padding |
| **FORMAT** | O1-O3 | Answer extraction, format mismatch, truncation |
| **OTHER** | X1-X3 | Unclassified, multiple errors, novel patterns |

---

## Phase 4: Preliminary Coding Results

### Sample Coded (n=23 errors)

#### Primary Category Distribution
| Category | Count | Percentage |
|----------|-------|------------|
| FACTUAL | 7 | 30.4% |
| PROCEDURAL | 5 | 21.7% |
| LOGIC | 4 | 17.4% |
| RLHF_PATTERN | 3 | 13.0% |
| COMPREHENSION | 3 | 13.0% |
| FORMAT | 1 | 4.3% |

#### Subtype Distribution (Top 5)
| Subtype | Count | Description |
|---------|-------|-------------|
| P2 | 4 | Wrong method |
| L1 | 4 | Invalid deduction |
| F3 | 3 | Concept misapplication |
| F1 | 2 | Hallucination |
| M1 | 2 | Misread question |

#### Confidence Distribution
| Confidence | Count | Percentage |
|------------|-------|------------|
| High | 17 | 73.9% |
| Medium | 6 | 26.1% |
| Low | 0 | 0% |

### RLHF Pattern Analysis
All 3 RLHF_PATTERN errors came from **RLHF models**:
- **R1 (Persuasive Incorrect):** 1 error - Elaborate reasoning, wrong conclusion
- **R5 (False Correction):** 2 errors - Self-corrects from right to wrong

---

## Phase 5: Rubric Refinement Recommendations

### Based on Testing

1. **LOGIC vs FACTUAL boundary:** Some errors blur these categories. Consider adding decision criteria:
   - If error is about *what is true* → FACTUAL
   - If error is about *what follows* → LOGIC

2. **RLHF_PATTERN specificity:** R5 (False Correction) appears distinctively in RLHF models. Consider splitting:
   - R5a: Self-correction with hedging language
   - R5b: Self-correction with false confidence

3. **Multiple error handling:** Many errors span categories. Current approach:
   - Primary = main failure mode
   - Secondary = contributing factor
   - Consider weighted scoring for analysis

### For Full Collection Coding

1. **Code all 80 errors** using the refined rubric
2. **Inter-rater reliability:** Have second coder classify 20% sample
3. **Calculate Cohen's κ** for primary category agreement
4. **Refine definitions** based on disagreement analysis

---

## Files Generated

| File | Location | Purpose |
|------|----------|---------|
| `error_collection.csv` | `/errors/` | Full 80-error dataset with problem text, responses, solutions |
| `error_collection_summary.txt` | `/errors/` | Distribution statistics |
| `error_examples.txt` | `/errors/` | Readable sample of first 5 errors |
| `error_classification_rubric.md` | `/analysis/` | Full rubric with categories, subtypes, examples |
| `error_coding_spreadsheet.csv` | `/analysis/` | Coding template with preliminary codes |
| `coding_summary.txt` | `/analysis/` | Preliminary coding statistics |
| `rubric_development_report.md` | `/analysis/` | This document |

---

## Next Steps

1. **Complete coding:** Code remaining 57 errors using rubric
2. **Inter-rater testing:** Second coder classifies 16 errors (20%)
3. **Calculate reliability:** Compute Cohen's κ for primary categories
4. **Refine rubric:** Update definitions based on reliability analysis
5. **Full analysis:** Analyze error patterns by model group and problem type

---

## Rubric Access

The full error classification rubric is available at:
`/analysis/error_classification_rubric.md`

The coding spreadsheet for ongoing work:
`/analysis/error_coding_spreadsheet.csv`

---

## References

- U-SOPHISTRY literature on RLHF-associated error patterns [19], [20]
- Open coding methodology from grounded theory
- Stratified sampling for representative error collection
