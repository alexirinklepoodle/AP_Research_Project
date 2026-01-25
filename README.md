# AP Research: RLHF vs Non-RLHF LLM Error Analysis

## Project Overview
This repository contains the complete code and data for an AP Research project investigating how Reinforcement Learning with Human Feedback (RLHF) affects the qualitative error patterns of Large Language Models on complex reasoning tasks. The study compares RLHF-aligned models against non-RLHF alternatives using a mixed-methods quasi-experimental design.

## Current Project Structure
```
AP_Research_Project/
├── problems/                    # Problem datasets
│   ├── problems.csv            # MAIN: Combined HLE+MMLU (350 problems)
│   ├── summaries/              # Statistical summaries and analyses
│   │   ├── combined_summary.csv
│   │   ├── hle_summary.csv
│   │   ├── subject_level_summary.csv
│   │   └── subject_breakdown.csv
│   └── archive/                # Backup and historical files
│       ├── problems_hle.csv
│       ├── problems_mmlu_only.csv
│       └── problems_mmlu_original.csv
│
├── scripts/                    # Python code for the study
│   ├── data_collector.py       # Main data collection script (phased approach)
│   ├── scoring_engine.py       # Scores LLM responses against solutions
│   ├── analysis_tools.py       # Statistical analysis and visualizations
│   ├── build_college_mmlu.py   # Creates MMLU college-level problem set
│   ├── build_hle_problems.py   # Creates HLE problem set (requires HF token)
│   ├── combine_problems_fixed.py # Safely combines HLE and MMLU datasets
│   └── old_versions/           # Deprecated scripts (for reference)
│
├── data/                       # Generated data (created automatically)
│   ├── raw/                    # Raw LLM responses with timestamps
│   └── processed/              # Scored and analyzed data
│
├── logs/                       # Run logs and error tracking
├── visualizations/             # Charts, graphs, and analysis outputs
├── backups/                    # Automatic and manual backups
├── .gitignore                  # Git ignore rules
└── PROJECT_STRUCTURE.md        # Detailed project documentation
```

## Core Methodology

### **Dataset Composition**
- **Total Problems:** 350 complex reasoning tasks
- **HLE (Humanity's Last Exam):** 150 advanced STEM problems (Math, Physics, Engineering, Chemistry, Biology/Medicine, CS/AI)
- **MMLU (Massive Multitask Language Understanding):** 200 college-level STEM problems
- **Filtering:** Excludes high school/elementary subjects to ensure appropriate difficulty

### **Model Testing Strategy (Phased Approach)**
- **Phase 1 (Core Comparison):** 
  - RLHF Group: `llama3.1:8b-instruct`
  - Non-RLHF Group: `mistral:7b-instruct-v0.3`
  
- **Phase 2 (Scale Comparison):**
  - RLHF Group: `llama3.2:1b-instruct` (1.4B parameters)
  - Non-RLHF Group: `gemma2:2b` (2.6B parameters, SFT-only)

## Updated Workflow

### **1. Dataset Preparation**
```bash
# Build MMLU college-level problem set
python3 scripts/build_college_mmlu.py

# (Optional) Build HLE problem set (requires HF_TOKEN)
export HF_TOKEN="your_token_here"
python3 scripts/build_hle_problems.py

# Combine datasets
python3 scripts/combine_problems_fixed.py
```

### **2. Model Preparation**
```bash
# Pull required models (adjust for current phase)
ollama pull llama3.1:8b-instruct
ollama pull mistral:7b-instruct-v0.3
ollama pull llama3.2:1b-instruct   # Phase 2 only
ollama pull gemma2:2b              # Phase 2 only
```

### **3. Data Collection**
```bash
# Set phase in scripts/data_collector.py (line with CURRENT_PHASE)
# Options: 1 = Core only, 2 = Core + Scale comparison

# Run data collection
python3 scripts/data_collector.py
```

### **4. Analysis & Scoring**
```bash
# Scoring happens automatically during data collection
# Results are saved to data/processed/

# For additional analysis and visualizations
python3 scripts/analysis_tools.py
```

## Configuration

### **Phased Approach Control**
In `scripts/data_collector.py`, control which models run:
```python
# Set to 1 for core comparison only, 2 for including scale comparison
CURRENT_PHASE = 2
```

### **Problem Set Configuration**
- Problems are stored in `problems/problems.csv`
- Each problem includes: ID, type, text, solution, reasoning, source (HLE/MMLU)
- Summaries are automatically generated in `problems/summaries/`

## Expected Outputs

### **Data Collection**
- Raw responses in `data/raw/` (timestamped CSV files)
- Automatic scoring against reference solutions
- Error categorization and frequency counts

### **Analysis**
- Quantitative: Error rates, statistical tests (t-tests, chi-square)
- Qualitative: Error patterns, reasoning chain analysis
- Visualizations: Comparative charts, error distribution graphs

## Research Design Notes

### **Controlled Variables**
- Model architecture: Decoder-only Transformer
- Parameter scale: Paired comparisons (8B/7B, 1.4B/2.6B)
- Prompt format: Identical across all models
- Temperature: Fixed at 0 for deterministic outputs
- Chain-of-thought prompting: "Let's think step by step"

### **Validity Measures**
- Cohort balancing for internal validity
- Identical stimuli and controlled prompting
- Iterative rubric development for qualitative coding
- Intra-rater reliability assessment (Cohen's κ > 0.7)

## Technical Requirements

- **Python:** 3.8+
- **Ollama:** Latest version with required models pulled
- **Python Packages:** pandas, datasets, matplotlib, numpy
- **Storage:** ~10GB for models, ~2GB for data
- **Memory:** 16GB+ RAM recommended for 7B+ models

## For AP Research Documentation

This project implements a quasi-experimental mixed-methods design. All methodological choices, including dataset selection, model pairing, and phased testing, are documented in the research paper and method log. The code structure ensures reproducibility and transparency for academic evaluation.

---

*Last Updated: January 2025*  
*AP Research Project: LLM Error Analysis*