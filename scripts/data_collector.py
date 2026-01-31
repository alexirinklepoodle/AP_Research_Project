"""
AP RESEARCH: LLM Data Collection Script
Min Script ot run complete data collection pipeline
"""

import json
import csv 
import time 
import subprocess 
from datetime import datetime 
import os 

# import modules
from scoring_engine import score_responses
from analysis_tools import calculate_stats, find_patterns

def query_ollama(Model_name, prompt, max_entries = 3):
    """
    Query a local Ollama model with retry logic
    Returns repsponse text or error message
    """
    for attempt in range(max_entries):
        try:
            print(f" Querying {model_name} (attempt {attempt + 1})...")

            #Build command
            cmd = ['ollama', 'run', model_name, prompt]

            #Run with timeout
            result = subprocess.run(
                cmd, 
                capture_output = True,
                text = True,
                timeout = 120, #2 minute timeout
                encoding = 'utf-8'
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"    Error: {result.stderr[:100]}...")
                time.sleep(2) #wait before retry again

        except subprocess.TimeoutExpired:
            print(f"    TImeout after 120 seconds")
            time.sleep(5)
        except Exception as e:
            print(f"    Unexpected error: {str(e)}")
            time.sleep(3)

    return "ERROR: Failed after all retries"

def collect_data():
    """
    Main data collection function
    """

    print("=" * 60)
    print("AP RESEARCH: LLM Data Collection")
    print("=" * 60)

    #create directories if they don't exist
    os.makedirs("data/raw", exist_ok = True)
    os.makedirs("data/processed", exist_ok = True)
    os.makedirs("logs", exist_ok = True)

    #define models
    # ===== MODEL CONFIGURATION - PHASED APPROACH =====
    # PHASE 1: Core 8B Comparison (Original Setup)
    models_phase1 = [
        {"name": "llama3.1:8b-instruct", "group": "RLHF", "phase": 1, "note": "Primary RLHF 8B"},
        {"name": "mistral:7b-instruct-v0.3", "group": "non-RLHF", "phase": 1, "note": "SFT baseline 7B"},
    ]

    # PHASE 2: Small-Scale Comparison (Adds scale dimension)
    models_phase2 = [
        {"name": "llama3.2:1b-instruct", "group": "RLHF", "phase": 2, "note": "Small-scale RLHF 1.4B"},
        {"name": "gemma2:2b", "group": "non-RLHF", "phase": 2, "note": "Small-scale SFT-only 2.6B"},
    ]

    # ===== SELECT WHICH PHASE TO RUN =====
    # Change this variable to control which models run
    CURRENT_PHASE = 1  # Set to 1 or 2

    # Combine models based on current phase
    if CURRENT_PHASE == 1:
        models = models_phase1
        print("Running PHASE 1: Core 8B/7B comparison only")
    elif CURRENT_PHASE == 2:
        models = models_phase1 + models_phase2
        print("Running PHASE 1 + 2: Core + Small-scale comparison")
    else:
        models = models_phase1
        print("Invalid phase. Running PHASE 1 only")

    #load problems
    try:
        with open('problems/problems.csv', 'r', encoding = 'utf-8') as f:
            reader = csv.DictReader(f)
            problems = list(reader)
        print(f"✓ Loaded {len(problems)} problems from problems.csv")
    except FileNotFoundError:
        print("✗ ERROR: problems.csv not found in 'problems/' folder")
        print("Please create this file first (see create_problems.py)")
        return

    #prepare results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"data/raw/results_{timestamp}.csv"

    with open(results_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'timestamp', 'problem_id', 'problem_type', 'model_name', 
            'model_group', 'prompt', 'response', 'response_length'
        ])
        
        # Run through all combinations
        total_runs = len(problems) * len(models)
        current_run = 0
        
        for problem in problems:
            problem_id = problem['id']
            problem_type = problem['type']
            prompt_text = f"Solve this problem step by step. Show your reasoning clearly before giving the final answer.\n\nProblem: {problem['text']}\n\nLet's think step by step."
            
            for model_info in models:
                current_run += 1
                model_name = model_info['name']
                model_group = model_info['group']
                
                print(f"\n[{current_run}/{total_runs}] {model_name} on problem {problem_id} ({problem_type})")
                
                # Query the model
                start_time = time.time()
                response = query_ollama(model_name, prompt_text)
                elapsed = time.time() - start_time
                
                # Save the result
                writer.writerow([
                    datetime.now().isoformat(),
                    problem_id,
                    problem_type,
                    model_name,
                    model_group,
                    prompt_text,
                    response,
                    len(response)
                ])
                f.flush()  # Save after each
                
                print(f"  ✓ Response ({len(response)} chars, {elapsed:.1f}s)")
                
                # Be nice to the system
                time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"DATA COLLECTION COMPLETE!")
    print(f"Results saved to: {results_file}")
    print(f"{'='*60}")
    
    # Now score the results
    print("\nStarting scoring process...")
    scored_file = score_responses(results_file)
    
    # Calculate statistics
    print("\nCalculating statistics...")
    stats = calculate_stats(scored_file)
    
    # Find patterns
    print("\nAnalyzing error patterns...")
    patterns = find_patterns(scored_file)
    
    return results_file, scored_file

if __name__ == "__main__":
    collect_data()