"""
Score LLM responses against reference solutions
"""

import csv
import re
import json
import os
from datetime import datetime

def extract_final_answer(response):
    """
    Try to extract the final answer from a model response
    Looks for patterns like "The answer is X", "X", "Therefore X", etc.
    """
    # Common patterns for final answers
    patterns = [
        r'[Tt]he answer is[:\s]*([^\n\.]+)',
        r'[Ff]inal answer[:\s]*([^\n\.]+)',
        r'[Tt]herefore[,\s]*([^\n\.]+)',
        r'[Ss]o[,\s]*([^\n\.]+)',
        r'Answer[:\s]*([^\n\.]+)',
        r'[\n\s]([A-Za-z0-9\$\.,]+)[\.\n]'  # Last significant token before period or newline
    ]
    
    response_lower = response.lower()
    
    for pattern in patterns:
        match = re.search(pattern, response)
        if match:
            answer = match.group(1).strip()
            # Clean up common prefixes
            answer = re.sub(r'^[iis\:\-\s]*', '', answer)
            return answer
    
    # If no pattern matches, try to get the last non-empty line
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    if lines:
        return lines[-1]
    
    return "NO_ANSWER_EXTRACTED"

def is_correct(model_answer, reference_answer, problem_type):
    """
    Compare model answer to reference answer
    Returns: 1 for correct, 0 for incorrect, 0.5 for partial
    """
    # Clean both answers
    model_clean = str(model_answer).lower().strip()
    ref_clean = str(reference_answer).lower().strip()
    
    # Remove common punctuation
    for char in ['.', ',', ';', ':', '!', '?', '$', '€', '£']:
        model_clean = model_clean.replace(char, '')
        ref_clean = ref_clean.replace(char, '')
    
    # Exact match
    if model_clean == ref_clean:
        return 1
    
    # For math problems, try numeric comparison
    if problem_type == 'math':
        # Extract numbers
        model_nums = re.findall(r'\d+\.?\d*', model_clean)
        ref_nums = re.findall(r'\d+\.?\d*', ref_clean)
        
        if model_nums and ref_nums:
            # Compare the last number found (often the final answer)
            if model_nums[-1] == ref_nums[-1]:
                return 1
    
    # Contains reference answer
    if ref_clean in model_clean:
        return 1
    
    # Reference contains model answer (for shorter responses)
    if model_clean and model_clean in ref_clean:
        return 1
    
    return 0

def score_responses(raw_results_file):
    """
    Score all responses in a results file
    """
    print(f"Scoring responses from {raw_results_file}")
    
    # Load problems with solutions
    problems = {}
    try:
        with open('problems/problems.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                problems[row['id']] = {
                    'solution': row['solution'],
                    'reasoning': row['reasoning'],
                    'type': row['type']
                }
    except FileNotFoundError:
        print("✗ ERROR: problems.csv not found")
        return None
    
    # Create scored results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scored_file = f"data/processed/scored_{timestamp}.csv"
    
    with open(raw_results_file, 'r', encoding='utf-8') as infile, \
         open(scored_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + [
            'extracted_answer', 'reference_answer', 'score', 
            'score_binary', 'notes'
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        scored_count = 0
        correct_count = 0
        
        for row in reader:
            problem_id = row['problem_id']
            
            if problem_id not in problems:
                print(f"  Warning: No solution found for problem {problem_id}")
                continue
            
            # Extract answer from model response
            extracted = extract_final_answer(row['response'])
            
            # Get reference solution
            reference = problems[problem_id]['solution']
            problem_type = problems[problem_id]['type']
            
            # Score the response
            score = is_correct(extracted, reference, problem_type)
            score_binary = 1 if score >= 0.5 else 0
            
            if score_binary == 1:
                correct_count += 1
            
            # Add scoring results to row
            row['extracted_answer'] = extracted
            row['reference_answer'] = reference
            row['score'] = score
            row['score_binary'] = score_binary
            row['notes'] = ""
            
            writer.writerow(row)
            scored_count += 1
    
    accuracy = (correct_count / scored_count * 100) if scored_count > 0 else 0
    
    print(f"✓ Scored {scored_count} responses")
    print(f"✓ Accuracy: {correct_count}/{scored_count} ({accuracy:.1f}%)")
    print(f"✓ Results saved to: {scored_file}")
    
    return scored_file

if __name__ == "__main__":
    # Test with the most recent results file
    import glob
    # Look for multiple patterns
    results_files = (
        glob.glob("data/raw/results_*.csv") +
        glob.glob("data/raw/*_results_*.csv") +
        glob.glob("data/raw/*.csv")
    )
    # Remove duplicates and sort by modification time
    results_files = list(set(results_files))
    if results_files:
        latest = max(results_files, key=os.path.getmtime)
        score_responses(latest)
    else:
        print("No results files found in data/raw/")