"""
AP Research - Dataset Exploration Script
Loads and inspects TACO, ARC-Challenge, and HellaSwag datasets.
Run from project root: python3 scripts/explore_datasets.py
"""

from datasets import load_dataset
import json

def explore_taco():
    """Load and examine the TACO dataset."""
    print("\n" + "="*60)
    print("EXPLORING TACO DATASET")
    print("="*60)
    
    try:
        # Load the TACO dataset (using the 'test' split is standard for evaluation)
        taco_dataset = load_dataset("BAAI/TACO", split="test")
        print(f"✓ Loaded TACO. Total problems in test set: {len(taco_dataset)}")
        
        # Show a few samples with details
        print("\n--- Samples from TACO ---")
        for i in range(2):  # Look at first 2 problems
            sample = taco_dataset[i]
            print(f"\nSample {i+1}:")
            print(f"  ID/Index: {i}")
            print(f"  Difficulty: {sample['difficulty']}")
            print(f"  Skill Types: {sample['skill_types']}")
            print(f"  Question Preview: {sample['question'][:150]}...")
            
            # The 'solutions' field is a JSON string; parse it
            solutions_list = json.loads(sample['solutions'])
            print(f"  Number of Reference Solutions: {len(solutions_list)}")
            if solutions_list:
                print(f"  First Solution Preview: {solutions_list[0][:100]}...")
        
        # Count problems by difficulty
        print("\n--- Difficulty Breakdown ---")
        difficulties = {}
        for problem in taco_dataset:
            diff = problem['difficulty']
            difficulties[diff] = difficulties.get(diff, 0) + 1
        
        for diff, count in difficulties.items():
            print(f"  {diff}: {count} problems")
            
    except Exception as e:
        print(f"✗ Error loading TACO: {e}")

def explore_arc():
    """Load and examine the ARC-Challenge dataset."""
    print("\n" + "="*60)
    print("EXPLORING ARC-CHALLENGE DATASET")
    print("="*60)
    
    try:
        # Load ARC-Challenge (NOT ARC-Easy)
        arc_dataset = load_dataset("ai2_arc", "ARC-Challenge", split="test")
        print(f"✓ Loaded ARC-Challenge. Total problems: {len(arc_dataset)}")
        
        print("\n--- Samples from ARC-Challenge ---")
        for i in range(2):  # Look at first 2 problems
            sample = arc_dataset[i]
            print(f"\nSample {i+1}:")
            print(f"  ID/Index: {i}")
            print(f"  Question: {sample['question']}")
            
            # Choices are stored in a dict with a 'text' list
            choices = sample['choices']['text']
            print(f"  Answer Choices:")
            for j, choice in enumerate(choices):
                print(f"    {chr(65+j)}. {choice}")
            
            print(f"  Correct Answer Key: {sample['answerKey']} (Option {sample['answerKey']})")
            
    except Exception as e:
        print(f"✗ Error loading ARC: {e}")

def explore_hellaswag():
    """Load and examine the HellaSwag dataset."""
    print("\n" + "="*60)
    print("EXPLORING HELLASWAG DATASET")
    print("="*60)
    
    try:
        hellaswag_dataset = load_dataset("Rowan/hellaswag", split="test")
        print(f"✓ Loaded HellaSwag. Total problems: {len(hellaswag_dataset)}")
        
        print("\n--- Samples from HellaSwag ---")
        for i in range(2):  # Look at first 2 problems
            sample = hellaswag_dataset[i]
            print(f"\nSample {i+1}:")
            print(f"  ID/Index: {i}")
            print(f"  Context/Scenario: {sample['ctx']}")
            
            print(f"  Possible Endings:")
            endings = sample['endings']
            for j, ending in enumerate(endings):
                print(f"    {chr(65+j)}. {ending}")
            
            # Label is an integer (0, 1, 2, or 3)
            correct_idx = sample['label']
            print(f"  Correct Ending Index: {correct_idx} (Option {chr(65 + correct_idx)})")
            
    except Exception as e:
        print(f"✗ Error loading HellaSwag: {e}")

def main():
    """Main exploration function."""
    print("="*60)
    print("AP RESEARCH DATASET EXPLORER")
    print("="*60)
    print("This script loads and displays samples from three datasets.")
    print("You'll use this information to select your 80 research problems.")
    
    # Install check reminder
    print("\n⚠  REMINDER: Make sure you installed the library:")
    print("   Run in terminal: pip3 install datasets")
    
    # Explore each dataset
    explore_taco()
    explore_arc()
    explore_hellaswag()
    
    print("\n" + "="*60)
    print("EXPLORATION COMPLETE")
    print("="*60)
    print("\n📝 NEXT STEPS:")
    print("1. Review the output above to understand each dataset.")
    print("2. Note the structure: how questions, answers, and metadata are stored.")
    print("3. Decide on your mix (e.g., 50 TACO, 20 ARC, 10 HellaSwag).")
    print("4. You'll manually select specific problem indices next.")

if __name__ == "__main__":
    main()