# Qualitative Analysis Scripts - Quick Reference

## ✅ What's Been Created

A complete qualitative analysis pipeline for your AP Research project on RLHF vs non-RLHF LLM error patterns.

## 📁 New Scripts

### 1. **error_collection.py**
**Purpose:** Extract all incorrect responses and create stratified sample

**Run:**
```bash
python3 scripts/error_collection.py
```

**Outputs:**
- `error_collection_full_*.csv` - All 734 errors from your data
- `error_collection_sample_*.csv` - Stratified sample (81 errors)
- `error_collection_coding_*.csv` - Coding-ready format
- `error_summary_*.txt` - Summary statistics

---

### 2. **qualitative_rubric.py**
**Purpose:** Develop coding rubric through open coding

**Run:**
```bash
python3 scripts/qualitative_rubric.py
```

**Features:**
- Creates starter rubric with 8 common LLM error types
- Allows adding/removing categories
- Exports human-readable codebook
- Saves rubric as JSON

**Starter Categories:**
- LOGIC - Logical Reasoning Error
- CALCULATION - Calculation/Computation Error
- MISUNDERSTANDING - Problem Misunderstanding
- KNOWLEDGE - Factual Knowledge Error
- PROCEDURE - Procedural Error
- INCOMPLETE - Incomplete Reasoning
- FORMAT - Format/Expression Error
- HALLUCINATION - Hallucination/Fabrication

---

### 3. **qualitative_coding.py**
**Purpose:** Interactive interface for coding errors

**Run:**
```bash
python3 scripts/qualitative_coding.py
```

**Features:**
- Displays each error with problem, response, and solution
- Shows rubric for reference
- Allows coding primary + secondary error types
- Tracks confidence levels
- Supports adding notes
- Saves progress automatically

**Commands:**
- `<CATEGORY_ID> [secondary] [confidence]` - Code error
- `SHOW` - Show full text
- `RUBRIC` - Show rubric
- `SKIP` - Skip error
- `QUIT` - Save and quit

---

### 4. **reliability_check.py**
**Purpose:** Calculate intra-rater reliability (Cohen's κ)

**Run (Part 1 - Create subset):**
```bash
python3 scripts/reliability_check.py
```

**Wait 1-2 weeks!**

**Run (Part 2 - Calculate):**
```bash
python3 scripts/reliability_check.py --calculate \
  --recode-file <file> --metadata-file <file>
```

**Outputs:**
- Cohen's κ coefficient
- Interpretation (target: κ ≥ 0.7)
- Category-level agreement
- Disagreement analysis

---

### 5. **pattern_analysis.py**
**Purpose:** Quantitize coded data and perform statistical tests

**Run:**
```bash
python3 scripts/pattern_analysis.py
```

**Analyses:**
- Frequency counts by error type and model group
- Contingency tables (RLHF vs non-RLHF)
- Chi-square test of independence
- Cramér's V effect size
- Standardized residuals
- Key pattern identification

**Outputs:**
- `pattern_analysis_*.json` - Full results
- `pattern_analysis_report_*.txt` - Human-readable report

---

### 6. **qualitative_workflow.py**
**Purpose:** Guided workflow through all steps

**Run:**
```bash
python3 scripts/qualitative_workflow.py
```

**Features:**
- Interactive prompts for each step
- Prerequisite checking
- Step-by-step guidance
- Links to individual scripts

---

## 📊 Updated Scripts

### scoring_engine.py
- Fixed to handle your file naming pattern (`*_results_*.csv`)
- Successfully scored 1,400 responses (47.6% accuracy)

### analysis_tools.py
- Added `run_qualitative_analysis_workflow()` function
- Updated docstrings to reference qualitative pipeline

---

## 📖 Documentation

### docs/QUALITATIVE_WORKFLOW.md
Complete documentation covering:
- Step-by-step workflow instructions
- File reference guide
- Troubleshooting tips
- Methodology notes for your paper
- Quick reference commands

---

## 🚀 Getting Started

### Option 1: Guided Workflow (Recommended)
```bash
python3 scripts/qualitative_workflow.py
```
This will walk you through each step interactively.

### Option 2: Individual Steps
```bash
# Step 1: Extract errors (✅ Already done!)
python3 scripts/error_collection.py

# Step 2: Develop rubric
python3 scripts/qualitative_rubric.py

# Step 3: Code errors
python3 scripts/qualitative_coding.py

# Step 4: Wait 1-2 weeks, then check reliability
python3 scripts/reliability_check.py

# Step 5: Analyze patterns
python3 scripts/pattern_analysis.py
```

---

## 📈 Current Data Status

✅ **Data Collection:** Complete
- 1,400 responses collected (P3_FULL)

✅ **Scoring:** Complete
- 666 correct (47.6%)
- 734 errors available for analysis

✅ **Error Collection:** Complete
- Full collection: 734 errors
- Stratified sample: 81 errors
- Balanced across model groups (RLHF: 371, non-RLHF: 363)

⏳ **Next Step:** Qualitative coding

---

## 📋 Your Workflow

### Immediate (Today/This Week)
1. ✅ ~~Run error collection~~ (Done!)
2. Open `data/processed/error_collection_coding_*.csv`
3. Read through 10-15 errors
4. Note observed patterns
5. Run `qualitative_rubric.py` to create/modify rubric

### Short-term (This Week)
1. Start coding with `qualitative_coding.py`
2. Code in batches (20-30 errors per session)
3. Take notes on ambiguous cases
4. Complete all 81 errors

### Medium-term (2 Weeks)
1. Wait 1-2 weeks after completing coding
2. Run reliability check
3. Recode 25% subset
4. Calculate Cohen's κ
5. If κ ≥ 0.7, proceed to pattern analysis

### Long-term (After Reliability Check)
1. Run pattern analysis
2. Review statistical findings
3. Select prototypical examples
4. Link quant + qual findings
5. Write results section

---

## 📂 File Structure

```
AP_Research_Project/
├── scripts/
│   ├── error_collection.py       ← NEW
│   ├── qualitative_rubric.py     ← NEW
│   ├── qualitative_coding.py     ← NEW
│   ├── reliability_check.py      ← NEW
│   ├── pattern_analysis.py       ← NEW
│   ├── qualitative_workflow.py   ← NEW
│   ├── scoring_engine.py         ← UPDATED
│   └── analysis_tools.py         ← UPDATED
├── data/
│   ├── raw/
│   │   └── P*_FULL_results_*.csv
│   └── processed/
│       ├── scored_*.csv                    ← Created by scoring_engine.py
│       ├── error_collection_*.csv          ← Created by error_collection.py
│       ├── rubric.json                     ← Created by qualitative_rubric.py
│       ├── coded_errors_*.csv              ← Created by qualitative_coding.py
│       ├── recode_subset_*.csv             ← Created by reliability_check.py
│       ├── reliability_results_*.json      ← Created by reliability_check.py
│       └── pattern_analysis_*.json         ← Created by pattern_analysis.py
└── docs/
    └── QUALITATIVE_WORKFLOW.md   ← NEW (complete documentation)
```

---

## 🎯 Key Features

### Stratified Sampling
- Ensures representation across model groups AND problem types
- Proportional allocation based on error frequency
- ~60-80 errors for manageable coding workload

### Open Coding Support
- Starter rubric based on common LLM errors
- Easy to add/remove/modify categories
- Example tracking for each category

### Reliability Assessment
- Cohen's κ calculation
- Category-level agreement analysis
- Disagreement case identification
- Clear interpretation guidelines

### Pattern Analysis
- Chi-square tests for group differences
- Effect size calculation (Cramér's V)
- Standardized residuals for cell-level analysis
- Automated key finding identification

---

## 💡 Tips

1. **Coding takes time** - Plan for 2-3 hours total, broken into sessions
2. **Take breaks** - Code in 30-45 minute sessions to maintain focus
3. **Document decisions** - Use the notes field for ambiguous cases
4. **Wait period is critical** - Don't skip the 1-2 week wait before reliability check
5. **κ < 0.7 is okay** - It means refine your rubric, not that you failed
6. **Non-significant results are valid** - Report them honestly

---

## ❓ Questions?

- See `docs/QUALITATIVE_WORKFLOW.md` for detailed documentation
- Run individual scripts with `--help` for command-line options
- Check script docstrings for function documentation

---

**Good luck with your qualitative analysis!** 🎓
