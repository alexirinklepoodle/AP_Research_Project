# Model Error Classification Rubric

## Development Process

This rubric was developed through **open coding** of 80 stratified errors from model responses across RLHF and non-RLHF model groups. Categories emerged inductively from observed patterns rather than being pre-specified.

---

## Primary Error Categories

### 1. LOGIC - Logic/Inferential Breakdown

**Definition:** Errors in reasoning where the model makes invalid deductions, exhibits internal contradictions, or violates logical rules.

**Subtypes:**

| Subtype | Description | Example |
|---------|-------------|---------|
| **L1: Invalid Deduction** | Conclusion doesn't follow from premises | "79.0 eV / 2 = 39.5 eV, so ionization energy is 39.5 eV" (removing one electron ≠ half the energy to remove both) |
| **L2: Internal Contradiction** | Model contradicts itself within response | States one answer but concludes with different answer |
| **L3: Circular Reasoning** | Uses conclusion as premise | "The answer is correct because it is the right choice" |
| **L4: Non Sequitur** | Jump in logic without justification | Abruptly switches topics or reasoning tracks |

**Example from Collection (E021):**
- Problem: Energy to ionize helium (remove 1 electron) given energy to remove both is 79.0 eV
- Model: "79.0 eV / 2 = 39.5 eV" → Answer B
- Error: Invalid deduction - ionization energy is NOT simply half; correct answer is 24.6 eV (A)

---

### 2. FACTUAL - Factual/Knowledge Deficiency

**Definition:** Model demonstrates incorrect domain knowledge, hallucinates facts, or misapplies concepts.

**Subtypes:**

| Subtype | Description | Example |
|---------|-------------|---------|
| **F1: Hallucination** | Invents non-existent facts/concepts | Claims molecule has functional groups it doesn't have |
| **F2: Incorrect Fact** | States factually wrong information | "Mars is closer to the sun than Earth" |
| **F3: Concept Misapplication** | Applies correct concept to wrong context | Uses wrong physics formula for scenario |
| **F4: Terminology Confusion** | Misuses technical terms | Confuses minimal polynomial with characteristic polynomial |

**Example from Collection (E002):**
- Problem: Identify byproduct of Diels-Alder reaction
- Model: Claims Molecule 1 "has a phenyl ring with chlorine" and is "an acyl chloride"
- Error: Hallucination - SMILES "COC1=CC=CCC1" is a methoxy-substituted diene, not an acyl chloride

---

### 3. PROCEDURAL - Procedural/Structural Error

**Definition:** Errors in problem-solving approach, including omitted steps, structural failures, or loss of constraints.

**Subtypes:**

| Subtype | Description | Example |
|---------|-------------|---------|
| **P1: Missing Step** | Skips essential reasoning step | Jumps to conclusion without intermediate derivation |
| **P2: Wrong Method** | Uses inappropriate solution approach | Applies differentiation when integration needed |
| **P3: Constraint Loss** | Forgets problem conditions | Ignores boundary conditions or domain restrictions |
| **P4: Incomplete Execution** | Starts correct method but doesn't finish | Sets up equation correctly but solves incorrectly |

**Example from Collection (E004):**
- Problem: Derive force per unit area using Maxwell's equations
- Model: Goes through 10 steps but arrives at wrong formula
- Error: Wrong method - misapplies boundary conditions and integration

---

### 4. CALCULATION - Simple Calculation Error

**Definition:** Basic arithmetic, algebraic, or computational mistakes within otherwise sound reasoning.

**Subtypes:**

| Subtype | Description | Example |
|---------|-------------|---------|
| **C1: Arithmetic Error** | Basic math mistake | 15/130 ≠ 0.1154 |
| **C2: Algebraic Error** | Symbolic manipulation mistake | Incorrect expansion or factorization |
| **C3: Unit Conversion** | Errors converting between units | Confuses eV, J, or other units |
| **C4: Sign Error** | Wrong positive/negative | Drops negative sign in calculation |

**Example from Collection (E023):**
- Problem: Calculate gate-source resistance
- Model: "15 / 0.1154" but doesn't complete calculation correctly
- Error: Arithmetic error in final computation

---

### 5. COMPREHENSION - Problem Misunderstanding

**Definition:** Model fundamentally misreads or misinterprets the problem statement.

**Subtypes:**

| Subtype | Description | Example |
|---------|-------------|---------|
| **M1: Misread Question** | Answers different question than asked | Asked for X but calculates Y |
| **M2: Option Confusion** | Confuses answer choices | Selects A when reasoning supports C |
| **M3: Symbol Misinterpretation** | Misreads mathematical/scientific notation | Misinterprets SMILES, equations, or symbols |
| **M4: Context Loss** | Loses track of problem context | Forgets initial conditions mid-solution |

**Example from Collection (E007):**
- Problem: Find maximal size of alien colony on chess board
- Model: Concludes "maximal size... is 8" (the initial count)
- Error: Misread question - asks for final colony size after expansion, not initial

---

### 6. RLHF_PATTERN - RLHF-Associated Pattern

**Definition:** Error patterns potentially associated with RLHF training, including persuasive but incorrect reasoning, excessive hedging, or sycophantic behaviors.

**Subtypes:**

| Subtype | Description | Example |
|---------|-------------|---------|
| **R1: Persuasive Incorrect** | Confident, well-structured but wrong | Elaborate step-by-step reasoning leading to incorrect answer |
| **R2: Excessive Hedging** | Over-qualifies and hedges before wrong answer | "However... upon closer inspection... actually..." then wrong |
| **R3: Sycophantic Reasoning** | Agrees with misleading problem premises | Doesn't challenge flawed assumptions in question |
| **R4: Verbose Padding** | Unnecessarily long response masking uncertainty | 10+ steps of reasoning for simple problem |
| **R5: False Correction** | "Corrects" itself to wrong answer | Starts with right approach, talks self into wrong answer |

**Example from Collection (E005):**
- Problem: Which curve has good ordinary reduction above 2?
- Model: 18+ lines of elaborate reasoning, eliminates options systematically, concludes A
- Error: Persuasive incorrect - confident, structured reasoning but wrong answer (E)

**Example from Collection (E019):**
- Problem: Order of group G with subgroup of order 7, no self-inverse elements
- Model: Correctly identifies 35 is divisible by 7, but selects 28 (not divisible by 7)
- Error: False correction - starts correct, talks self into wrong answer

---

### 7. FORMAT - Output/Format Error

**Definition:** Correct reasoning but fails to match required output format.

**Subtypes:**

| Subtype | Description | Example |
|---------|-------------|---------|
| **O1: Answer Extraction Failure** | Correct reasoning but wrong answer extracted | Boxed answer doesn't match conclusion |
| **O2: Format Mismatch** | Wrong answer format | Gives number when letter choice required |
| **O3: Truncation** | Response cut off before answer | Model stops before stating final answer |

---

### 8. OTHER - Unclassified Error

**Definition:** Errors that don't fit other categories.

**Subtypes:**

| Subtype | Description |
|---------|-------------|
| **X1: Ambiguous** | Cannot determine error type from available information |
| **X2: Multiple Errors** | Error spans multiple categories equally |
| **X3: Novel Pattern** | New error type not captured by rubric |

---

## Coding Instructions

### Step 1: Primary Category Assignment
Assign **one** primary error category that best captures the main failure mode:
- LOGIC
- FACTUAL
- PROCEDURAL
- CALCULATION
- COMPREHENSION
- RLHF_PATTERN
- FORMAT
- OTHER

### Step 2: Subtype Assignment
Assign the specific subtype (e.g., L1, F2, R4) that best describes the error.

### Step 3: Secondary Category (if applicable)
If error clearly spans two categories, assign a secondary category.

### Step 4: Confidence Rating
- **High:** Clear, unambiguous error pattern
- **Medium:** Probable pattern but some ambiguity
- **Low:** Uncertain classification

### Step 5: Notes
Document any additional observations, especially for edge cases.

---

## Decision Tree for Classification

```
START
│
├─ Does model misunderstand the problem? → COMPREHENSION
│
├─ Does model state incorrect facts/hallucinate? → FACTUAL
│
├─ Does model make arithmetic/computation error? → CALCULATION
│
├─ Does model use wrong method or skip steps? → PROCEDURAL
│
├─ Does model make invalid logical inference? → LOGIC
│
├─ Is response confident/elaborate but wrong? → RLHF_PATTERN
│  ├─ Excessive hedging/qualification? → R2
│  ├─ Talks self into wrong answer? → R5
│  └─ Verbose padding? → R4
│
├─ Is reasoning correct but output wrong format? → FORMAT
│
└─ None of above → OTHER
```

---

## Inter-Rater Reliability Guidelines

When multiple coders classify the same error:

1. **Primary category agreement:** Coders must agree on primary category
2. **Subtype flexibility:** Subtype disagreement acceptable if primary matches
3. **Discussion threshold:** Discuss any errors where confidence < Medium
4. **Consensus process:** Third coder breaks ties

---

## Example Coded Errors

| Error ID | Model | Primary | Subtype | Secondary | Confidence | Notes |
|----------|-------|---------|---------|-----------|------------|-------|
| E001 | codellama:7b | FACTUAL | F3 | LOGIC | High | Misapplies surface energy concept |
| E002 | llama3.1:8b | FACTUAL | F1 | COMPREHENSION | High | Hallucinates molecular structure |
| E004 | llama3.1:8b | PROCEDURAL | P2 | - | Medium | Wrong boundary condition application |
| E005 | llama3.1:8b | RLHF_PATTERN | R1 | LOGIC | High | Elaborate but incorrect elimination |
| E007 | codellama:7b | COMPREHENSION | M1 | - | High | Answers wrong question |
| E019 | llama3.1:8b | RLHF_PATTERN | R5 | LOGIC | High | Self-corrects to wrong answer |
| E021 | codellama:7b | LOGIC | L1 | - | High | Invalid division reasoning |

---

## Version History

- **v1.0** - Initial rubric from open coding of 80 errors
- Categories derived inductively from error patterns
- RLHF_PATTERN category added to capture alignment-associated behaviors

---

## References

[19], [20] - U-SOPHISTRY and RLHF-associated error pattern literature
