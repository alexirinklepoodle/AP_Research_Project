"""
Create and manage problem set for AP Research
"""

import csv
import random

def create_problem_set():
    """
    Create a CSV file with reasoning problems
    """
    problems = []
    
    # Example problems - replace these with your actual 80 problems
    # Math problems (like GSM8K)
    math_problems = [
        {
            "id": "M001",
            "type": "math",
            "text": "A train travels at 60 miles per hour for 2.5 hours. How far does it travel?",
            "solution": "150 miles",
            "reasoning": "Distance = speed × time = 60 mph × 2.5 hours = 150 miles.",
            "source": "GSM8K_adapted"
        },
        {
            "id": "M002",
            "type": "math", 
            "text": "If a shirt costs $25 and is on sale for 20% off, what is the sale price?",
            "solution": "$20",
            "reasoning": "20% of $25 is $5. $25 - $5 = $20.",
            "source": "GSM8K_adapted"
        }
    ]
    
    # Coding problems (like HumanEval)
    code_problems = [
        {
            "id": "C001",
            "type": "code",
            "text": "Write a Python function that reverses a string.",
            "solution": "def reverse_string(s): return s[::-1]",
            "reasoning": "Use Python slicing with step -1 to reverse the string.",
            "source": "HumanEval_adapted"
        }
    ]
    
    # Logic problems
    logic_problems = [
        {
            "id": "L001",
            "type": "logic",
            "text": "All birds have feathers. Penguins are birds. Therefore, penguins have feathers. Is this reasoning valid?",
            "solution": "Yes",
            "reasoning": "This is a valid syllogism: If all A are B, and C is an A, then C is B.",
            "source": "created"
        }
    ]
    
    # Combine all problems
    problems = math_problems + code_problems + logic_problems
    
    # Save to CSV
    with open('problems/problems.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'type', 'text', 'solution', 'reasoning', 'source']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(problems)
    
    print(f"✓ Created problems.csv with {len(problems)} problems")
    print("⚠  REMEMBER: Replace these example problems with your actual 80 research problems!")
    
    # Also create a template for your actual problems
    with open('problems/problem_template.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'type', 'text', 'solution', 'reasoning', 'source'])
        writer.writerow(['M001', 'math', 'Your problem text here...', 'Correct answer', 'Step-by-step reasoning', 'GSM8K/HumanEval/original'])
    
    print("✓ Created problem_template.csv for your actual problems")

def add_problem(problem_id, problem_type, text, solution, reasoning, source):
    """
    Add a single problem to the CSV
    """
    try:
        with open('problems/problems.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([problem_id, problem_type, text, solution, reasoning, source])
        print(f"✓ Added problem {problem_id}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    create_problem_set()