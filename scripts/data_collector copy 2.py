"""
AP RESEARCH: LLM Data Collection Script
Fixed version with proper Ollama integration
"""

import json
import csv 
import time 
import subprocess 
from datetime import datetime 
import os 

def query_ollama(model_name, prompt, max_retries=3):
    """
    Query a local Ollama model with retry logic
    Returns response text or error message
    """
    for attempt in range(max_retries):
        try:
            print(f"  Querying {model_name} (attempt {attempt + 1}/{max_retries})...", end=" ")

            # Build command - NO prompt in args!
            cmd = ['ollama', 'run', model_name]
            
            # Run with timeout, passing prompt via stdin
            result = subprocess.run(
                cmd, 
                input=prompt,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout
                encoding='utf-8'
            )

            if result.returncode == 0:
                # Clean up any terminal control characters
                response = result.stdout.strip()
                response = response.replace('\x1b[2K\r', '').replace('\x1b[1G', '').strip()
                print("✓")
                return response
            else:
                print(f"✗ Error code {result.returncode}")
                if result.stderr:
                    print(f"    Stderr: {result.stderr[:150]}...")
                time.sleep(2)  # Wait before retry

        except subprocess.TimeoutExpired:
            print("⏰ Timeout after 180 seconds")
            time.sleep(5)
        except Exception as e:
            print(f"⚠ Unexpected error: {str(e)[:100]}")
            time.sleep(3)

    return "ERROR: Failed after all retries"

def test_model_simple():
    """Quick test to verify Ollama is working"""
    print("\n🔧 Testing Ollama connection...")
    
    # Test with a simple prompt
    test_prompt = "Solve this step by step: A train travels 60 mph for 2.5 hours. How far does it travel?"
    
    print(f"  Testing llama3.2:1b with simple prompt...")
    response = query_ollama("llama3.2:1b", test_prompt, max_retries=1)
    
    if "ERROR" in response:
        print(f"  ✗ Test failed: {response}")
        return False
    else:
        print(f"  ✓ Test successful! Response: {response[:100]}...")
        return True

def collect_data():
    """
    Main data collection function
    """

    print("=" * 60)
    print("AP RESEARCH: LLM Data Collection")
    print("=" * 60)
    
    # Test Ollama first
    if not test_model_simple():
        print("\n❌ Ollama test failed. Please check:")
        print("   1. Is Ollama installed? (run 'ollama --version')")
        print("   2. Are models downloaded? (run 'ollama list')")
        print("   3. Is Ollama running? (check 'ollama serve' in another terminal)")
        return

    # Create directories if they don't exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Define models - Phase 3 only for now
    models = [
        {"name": "llama3.1:8b", "group": "RLHF", "note": "1.4 B parameters (scale down)"},
        {"name": "gemma2:2b", "group": "non-RLHF", "note": "Small-scale baseline (2.6 B)"},
    ]

    # Load problems
    try:
        with open('problems/problems.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            problems = list(reader)
        print(f"✓ Loaded {len(problems)} problems from problems.csv")
    except FileNotFoundError:
        print("✗ ERROR: problems.csv not found in 'problems/' folder")
        return

    # Ask for test mode
    print(f"\n⚠ You have {len(problems)} problems and {len(models)} models")
    print(f"  Full run: {len(problems)} × {len(models)} = {len(problems)*len(models)} queries")
    
    response = input("\nRun in TEST mode (first 5 problems only)? [y/n]: ").strip().lower()
    test_mode = response == 'y'
    
    if test_mode:
        max_problems = 5
        print(f"✓ Running TEST mode: First {max_problems} problems only")
    else:
        max_problems = len(problems)
        print(f"✓ Running FULL mode: All {max_problems} problems")
        print(f"  Estimated time: ~{max_problems * len(models) * 0.5:.0f} minutes")
        confirm = input("\nContinue with full run? [y/n]: ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            return

    # Prepare results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"data/raw/results_{timestamp}.csv"

    with open(results_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'timestamp', 'problem_id', 'problem_type', 'model_name', 
            'model_group', 'prompt', 'response', 'response_length', 'response_time_seconds'
        ])
        
        # Run through all combinations
        total_runs = min(max_problems, len(problems)) * len(models)
        current_run = 0
        start_time = time.time()
        
        for i, problem in enumerate(problems):
            if i >= max_problems:
                break
                
            problem_id = problem['id']
            problem_type = problem['type']
            
            # Create prompt with chain-of-thought
            prompt_text = f"""{problem['text']}

Please think through this problem step by step and provide your final answer.
Let's think step by step:"""
            
            for model_info in models:
                current_run += 1
                model_name = model_info['name']
                model_group = model_info['group']
                
                print(f"\n[{current_run}/{total_runs}] {model_name} on problem {problem_id} ({problem_type})")
                
                # Query the model
                query_start = time.time()
                response = query_ollama(model_name, prompt_text)
                query_time = time.time() - query_start
                
                # Save the result
                writer.writerow([
                    datetime.now().isoformat(),
                    problem_id,
                    problem_type,
                    model_name,
                    model_group,
                    prompt_text,
                    response,
                    len(response),
                    round(query_time, 2)
                ])
                f.flush()  # Save after each
                
                print(f"  ✓ Response ({len(response)} chars, {query_time:.1f}s)")
                if len(response) < 50:
                    print(f"  ⚠ Short response: {response}")
                
                # Be nice to the system - small delay between queries
                time.sleep(1)
    
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"DATA COLLECTION COMPLETE!")
    print(f"Results saved to: {results_file}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average per query: {total_time/total_runs:.1f} seconds")
    print(f"{'='*60}")
    
    # Show summary
    print("\n📊 Quick Summary:")
    print(f"  Problems tested: {min(max_problems, len(problems))}")
    print(f"  Models tested: {len(models)}")
    print(f"  Total queries: {total_runs}")
    
    # Check for errors
    import pandas as pd
    df = pd.read_csv(results_file)
    error_count = df['response'].str.contains('ERROR').sum()
    if error_count > 0:
        print(f"  ⚠ Errors found: {error_count} queries failed")
    else:
        print(f"  ✓ No errors detected")
    
    return results_file

if __name__ == "__main__":
    collect_data()