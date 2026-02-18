# Qualitative Analysis Workflow Documentation

## Overview

This documentation covers the **qualitative processing** phase of your AP Research project on RLHF vs non-RLHF LLM error patterns. This phase follows quantitative scoring and focuses on understanding the *types* of errors made by different model groups.

## Prerequisites

Before starting qualitative analysis, ensure you have:

- ✅ Completed data collection (all models run on all problems)
- ✅ Scored all responses using `scoring_engine.py`
- ✅ At least 50+ errors available for analysis

Check:
```bash
python3 scripts/scoring_engine.py
```

## The Qualitative Pipeline

The qualitative analysis consists of **6 sequential steps**:

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Error Collection → Extract & sample errors            │
│  STEP 2: Rubric Development → Create coding categories         │
│  STEP 3: Coding → Apply rubric to all errors                   │
│  STEP 4: Reliability Check → Verify coding consistency (κ)     │
│  STEP 5: Pattern Analysis → Statistical tests & visualization  │
│  STEP 6: Synthesis → Link quant + qual findings                │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

Run the guided workflow:
```bash
python3 scripts/qualitative_workflow.py
```

This interactive script will guide you through each step with prompts.

---

## Step 1: Error Collection

**Purpose:** Extract all incorrect responses and create a stratified sample for coding.

**What it does:**
- Loads your scored data
- Identifies all errors (score_binary = 0)
- Creates stratified sample (~60 errors) by model group and problem type
- Saves multiple formats for different uses

**Run:**
```bash
python3 scripts/error_collection.py
```

**Outputs:**
| File | Description |
|------|-------------|
| `error_collection_full_*.csv` | All errors (for reference) |
| `error_collection_sample_*.csv` | Stratified sample (~60 errors) |
| `error_collection_coding_*.csv` | Coding-ready format with blank fields |
| `error_summary_*.txt` | Summary statistics |

**Key parameters:**
- `target_sample_size=60` (default) - Adjust based on your time availability
- Stratification ensures representation across model groups and problem types

---

## Step 2: Rubric Development

**Purpose:** Create a coding rubric through open coding of errors.

**Methodology:**
1. **Open Coding:** Read 10-15 errors without pre-set categories
2. **Note Patterns:** Write down recurring error types you observe
3. **Formalize Categories:** Create the rubric with clear definitions
4. **Iterative Refinement:** Test on new errors and revise

**Run:**
```bash
python3 scripts/qualitative_rubric.py
```

**Starter Categories** (modify based on your data!):
| ID | Name | Definition |
|----|------|------------|
| LOGIC | Logical Reasoning Error | Invalid inference or contradiction in reasoning |
| CALCULATION | Calculation Error | Wrong math but correct setup |
| MISUNDERSTANDING | Problem Misunderstanding | Addresses wrong question |
| KNOWLEDGE | Factual Knowledge Error | States incorrect facts |
| PROCEDURE | Procedural Error | Uses wrong method |
| INCOMPLETE | Incomplete Reasoning | Skips critical steps |
| FORMAT | Format/Expression Error | Wrong answer format |
| HALLUCINATION | Hallucination | Invents facts/concepts |

**Outputs:**
| File | Description |
|------|-------------|
| `rubric.json` | Machine-readable rubric |
| `codebook_*.txt` | Human-readable codebook |

**Tips:**
- Don't force errors into categories - let categories emerge from data
- Merge categories that overlap significantly
- Keep definitions clear and mutually exclusive
- Add example errors to each category

---

## Step 3: Coding

**Purpose:** Apply the rubric to code each error for primary and secondary error types.

**Run:**
```bash
python3 scripts/qualitative_coding.py
```

**Interactive coding interface:**
```
Error 1/60
======================================================================
ERROR ID: E0001
Model: llama3.1:8b (RLHF)
Problem Type: mmlu_math
----------------------------------------------------------------------
PROBLEM:
[problem text...]
----------------------------------------------------------------------
MODEL RESPONSE:
[model response...]
----------------------------------------------------------------------
CORRECT SOLUTION:
[reference answer]
======================================================================

CODING RUBRIC
----------------------------------------------------------------------
[CALCULATION] Calculation/Computation Error
[LOGIC] Logical Reasoning Error
[KNOWLEDGE] Factual Knowledge Error
...
----------------------------------------------------------------------

Coding: CALC LOGIC high
  → Coded: Calculation/Computation Error + LOGIC (high)
```

**Commands:**
- `<category_id> [secondary] [confidence]` - Code error (e.g., `CALC LOGIC high`)
- `SHOW` - Show full error text
- `RUBRIC` - Show rubric
- `NOTES` - Add notes
- `SKIP` - Skip this error
- `QUIT` - Save and quit

**Outputs:**
| File | Description |
|------|-------------|
| `coded_errors_*.csv` | Fully coded dataset |

**Tips:**
- Code in focused sessions (30-45 min max)
- Take breaks between sessions
- Flag ambiguous cases with notes
- Review your first 10 codings after completing 30 to check consistency

---

## Step 4: Reliability Check

**Purpose:** Assess your coding consistency using intra-rater reliability (Cohen's κ).

**Methodology:**
1. Create 25% random subset of coded errors
2. **Wait 1-2 weeks** (critical for avoiding memory bias)
3. Recode the subset blindly (without seeing original codes)
4. Calculate Cohen's κ between original and recoded

**Run (Part 1 - Create subset):**
```bash
python3 scripts/reliability_check.py
```

**Wait 1-2 weeks!**

**Run (Part 2 - Calculate reliability):**
```bash
python3 scripts/reliability_check.py --calculate \
  --recode-file data/processed/recode_subset_*.csv \
  --metadata-file data/processed/recode_subset_*_metadata.json
```

**Interpretation (Landis & Koch, 1977):**
| κ Value | Interpretation | Action |
|---------|----------------|--------|
| < 0.40 | Poor/Fair | Revise rubric significantly |
| 0.40-0.60 | Moderate | Refine ambiguous categories |
| 0.60-0.80 | Substantial | Acceptable, minor refinements |
| > 0.80 | Almost Perfect | Excellent reliability |

**Threshold:** κ ≥ 0.7 is considered acceptable for proceeding.

**If κ < 0.7:**
1. Review disagreement cases
2. Identify which categories have low agreement
3. Refine category definitions
4. Consider merging problematic categories
5. Recode a subset and recalculate

**Outputs:**
| File | Description |
|------|-------------|
| `recode_subset_*.csv` | Subset for blind recoding |
| `reliability_results_*.json` | Statistical results |
| `reliability_results_*_report.txt` | Human-readable report |

---

## Step 5: Pattern Analysis

**Purpose:** Quantitize coded data and test for differences between model groups.

**What it does:**
- Converts qualitative codes to frequencies
- Creates contingency tables (RLHF vs non-RLHF)
- Performs chi-square tests
- Calculates effect sizes (Cramér's V)
- Identifies which error types drive differences

**Run:**
```bash
python3 scripts/pattern_analysis.py
```

**Statistical tests:**
- **Chi-square test:** Tests if error distributions differ by model group
- **Cramér's V:** Effect size (0.1=small, 0.3=medium, 0.5=large)
- **Standardized residuals:** Which cells differ from expected (|residual| > 2 = significant)

**Outputs:**
| File | Description |
|------|-------------|
| `pattern_analysis_*.json` | Full statistical results |
| `pattern_analysis_report_*.txt` | Human-readable report |

**Example findings:**
```
χ²(7) = 15.234
p = 0.033
Effect size (Cramér's V) = 0.287 (Medium effect)

Key Findings:
• RLHF models show significantly more HALLUCINATION errors than expected (residual = 2.34)
• non-RLHF models show significantly more CALCULATION errors than expected (residual = -2.12)
```

---

## Step 6: Synthesis & Documentation

**Purpose:** Link quantitative and qualitative findings for your research paper.

**Activities:**

### 1. Review Results
- Read `pattern_analysis_report_*.txt`
- Check statistical significance and effect sizes
- Identify major patterns

### 2. Select Prototypical Examples
For each major pattern, select 3-5 representative errors:
```
Example 1: RLHF Hallucination Error
Problem: [ID and text]
Model Response: [excerpt showing hallucination]
Correct Solution: [reference]
Error Type: HALLUCINATION
Why prototypical: Clearly invents a formula that doesn't exist
```

### 3. Create Visualizations
Suggested visualizations:
- Stacked bar chart: Error type distribution by model group
- Heatmap: Contingency table with residuals
- Example boxes: Prototypical errors with annotations

### 4. Link Quant + Qual
For each finding:
1. **Quantitative:** "RLHF models made more hallucination errors (χ² p < 0.05)"
2. **Qualitative:** "These errors typically involved inventing formulas or concepts"
3. **Example:** Show a prototypical hallucination error
4. **Interpretation:** "This suggests RLHF may prioritize confident-sounding answers over accuracy"

### 5. Organize Files
Create a structured repository:
```
qualitative_analysis/
├── error_collection/
│   ├── error_collection_full.csv
│   └── error_summary.txt
├── rubric/
│   ├── rubric.json
│   └── codebook.pdf
├── coded_data/
│   ├── coded_errors.csv
│   └── reliability_results.pdf
├── analysis/
│   ├── pattern_analysis_report.pdf
│   └── visualizations/
└── examples/
    ├── rlhf_hallucination_examples.md
    └── non_rlhf_calculation_examples.md
```

---

## File Reference

### Input Files
| File | Source |
|------|--------|
| `data/processed/scored_*.csv` | From scoring_engine.py |
| `problems/problems.csv` | Your problem dataset |

### Output Files (in order of creation)
| File | From Script | Purpose |
|------|-------------|---------|
| `error_collection_*.csv` | error_collection.py | Errors to code |
| `rubric.json` | qualitative_rubric.py | Coding scheme |
| `coded_errors_*.csv` | qualitative_coding.py | Coded data |
| `recode_subset_*.csv` | reliability_check.py | Reliability sample |
| `reliability_results_*.json` | reliability_check.py | κ statistics |
| `pattern_analysis_*.json` | pattern_analysis.py | Statistical tests |
| `pattern_analysis_report_*.txt` | pattern_analysis.py | Findings report |

---

## Troubleshooting

### "No scored data found"
Run scoring_engine.py first:
```bash
python3 scripts/scoring_engine.py
```

### "No errors found"
Check your scored data - all responses may be correct. Verify:
```python
import pandas as pd
df = pd.read_csv('data/processed/scored_*.csv')
print((df['score_binary'] == 0).sum())
```

### "Cohen's κ is low (< 0.7)"
1. Review disagreement cases in reliability report
2. Identify which categories have lowest agreement
3. Refine definitions or merge overlapping categories
4. Recode and recalculate

### "Chi-square not significant"
This is a valid finding! It means:
- Error patterns don't differ between RLHF and non-RLHF models
- OR sample size is too small to detect differences
- OR differences are subtle

Report the effect size and confidence intervals.

### "Not enough time to code"
- 60 errors takes ~2-3 hours for careful coding
- Break into multiple sessions (20 errors/session)
- The stratified sample ensures you can generalize from fewer errors

---

## Methodology Notes for Your Paper

### Coding Process
Document:
- Number of errors coded
- Time spent coding
- Number of coding sessions
- Any ambiguous cases and how resolved

### Reliability
Report:
- Cohen's κ value
- Interpretation (e.g., "substantial agreement")
- Number of disagreements
- Any rubric revisions made

### Statistical Tests
Report:
- χ² value with degrees of freedom
- p-value
- Effect size (Cramér's V)
- Which error types differed significantly

### Validity Measures
- Triangulation: Link quant and qual findings
- Thick description: Provide detailed examples
- Reflexivity: Note your coding decisions and biases

---

## Quick Reference Commands

```bash
# Full workflow (interactive)
python3 scripts/qualitative_workflow.py

# Individual steps
python3 scripts/error_collection.py
python3 scripts/qualitative_rubric.py
python3 scripts/qualitative_coding.py
python3 scripts/reliability_check.py
python3 scripts/pattern_analysis.py

# View coded data summary
python3 -c "
import pandas as pd
import glob
files = glob.glob('data/processed/coded_errors_*.csv')
df = pd.read_csv(max(files))
print(df['primary_error_type'].value_counts())
"
```

---

## Next Steps After Qualitative Analysis

1. **Create final visualizations** for your paper
2. **Write results section** linking quant + qual findings
3. **Select examples** for appendix or main text
4. **Organize repository** for submission/supplementary materials
5. **Document methodology** in your methods section

---

## Questions?

Review the individual script docstrings for more details:
```bash
python3 -c "import error_collection; help(error_collection)"
```

Or consult your research advisor for methodology questions.
