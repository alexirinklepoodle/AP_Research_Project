"""
Qualitative Rubric Development Tool

This script supports the iterative development of a qualitative coding rubric:
1. Open coding: Read errors and note patterns without pre-set categories
2. Draft initial error categories based on observed patterns
3. Refine categories through iterative testing
4. Finalize rubric with clear definitions and example errors

Outputs:
- rubric.json: Formal rubric with categories, definitions, and examples
- coding_template.csv: Template for applying the rubric
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional

class QualitativeRubric:
    """Manages the development and storage of qualitative coding rubric"""
    
    def __init__(self, rubric_file: str = 'data/processed/rubric.json'):
        self.rubric_file = rubric_file
        self.categories = {}
        self.metadata = {
            'created': None,
            'last_modified': None,
            'version': 1,
            'coding_rounds': 0
        }
        self.load()
    
    def load(self) -> bool:
        """Load existing rubric if available"""
        if os.path.exists(self.rubric_file):
            with open(self.rubric_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.categories = data.get('categories', {})
                self.metadata = data.get('metadata', self.metadata)
            print(f"✓ Loaded existing rubric from {self.rubric_file}")
            print(f"  Categories: {len(self.categories)}")
            print(f"  Version: {self.metadata.get('version', 1)}")
            return True
        return False
    
    def add_category(self, category_id: str, name: str, definition: str, 
                     examples: List[str] = None, notes: str = ""):
        """
        Add or update a error category
        
        Args:
            category_id: Short identifier (e.g., 'LOGIC', 'CALCULATION')
            name: Human-readable name
            definition: Clear definition of what constitutes this error
            examples: List of example error texts
            notes: Additional notes about the category
        """
        self.categories[category_id] = {
            'name': name,
            'definition': definition,
            'examples': examples or [],
            'notes': notes,
            'count': 0  # Will be updated during coding
        }
        self.metadata['last_modified'] = datetime.now().isoformat()
        print(f"✓ Added category: {category_id} - {name}")
    
    def remove_category(self, category_id: str):
        """Remove a category"""
        if category_id in self.categories:
            del self.categories[category_id]
            self.metadata['last_modified'] = datetime.now().isoformat()
            print(f"✓ Removed category: {category_id}")
    
    def add_example(self, category_id: str, example_text: str, error_id: str = ""):
        """Add an example error to a category"""
        if category_id in self.categories:
            example = {
                'text': example_text,
                'error_id': error_id,
                'added': datetime.now().isoformat()
            }
            self.categories[category_id]['examples'].append(example)
            self.metadata['last_modified'] = datetime.now().isoformat()
    
    def view_categories(self):
        """Display all categories with definitions"""
        print("\n" + "=" * 70)
        print("QUALITATIVE CODING RUBRIC")
        print("=" * 70)
        
        if not self.categories:
            print("\nNo categories defined yet.")
            print("Use add_category() to create error categories based on your open coding.")
            return
        
        for cat_id, cat_data in sorted(self.categories.items()):
            print(f"\n[{cat_id}] {cat_data['name']}")
            print("-" * 70)
            print(f"Definition: {cat_data['definition']}")
            if cat_data.get('notes'):
                print(f"Notes: {cat_data['notes']}")
            if cat_data.get('examples'):
                examples = cat_data['examples']
                if isinstance(examples[0], dict):
                    examples = [e['text'] for e in examples]
                print(f"Examples ({len(examples)}):")
                for i, ex in enumerate(examples[:3], 1):  # Show first 3
                    ex_preview = ex.replace('\n', ' ')[:100]
                    print(f"  {i}. \"{ex_preview}...\"")
                if len(examples) > 3:
                    print(f"  ... and {len(examples) - 3} more")
        
        print("\n" + "=" * 70)
        print(f"Total categories: {len(self.categories)}")
        print(f"Version: {self.metadata.get('version', 1)}")
        print(f"Last modified: {self.metadata.get('last_modified', 'N/A')}")
    
    def save(self):
        """Save rubric to file"""
        os.makedirs(os.path.dirname(self.rubric_file), exist_ok=True)
        
        data = {
            'categories': self.categories,
            'metadata': self.metadata
        }
        
        with open(self.rubric_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Rubric saved to {self.rubric_file}")
    
    def export_codebook(self, output_file: str = None):
        """Export rubric as a human-readable codebook"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'data/processed/codebook_{timestamp}.txt'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("QUALITATIVE CODING CODEBOOK\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Version: {self.metadata.get('version', 1)}\n\n")
            
            f.write("INSTRUCTIONS\n")
            f.write("-" * 70 + "\n")
            f.write("1. Read each error carefully\n")
            f.write("2. Identify the PRIMARY error type (most significant issue)\n")
            f.write("3. If applicable, identify a SECONDARY error type\n")
            f.write("4. Record your confidence (high/medium/low)\n")
            f.write("5. Add notes for ambiguous cases\n\n")
            
            f.write("ERROR CATEGORIES\n")
            f.write("-" * 70 + "\n\n")
            
            for cat_id, cat_data in sorted(self.categories.items()):
                f.write(f"[{cat_id}] {cat_data['name']}\n")
                f.write(f"Definition: {cat_data['definition']}\n")
                if cat_data.get('notes'):
                    f.write(f"Notes: {cat_data['notes']}\n")
                
                examples = cat_data.get('examples', [])
                if examples:
                    f.write("\nExample Errors:\n")
                    for i, ex in enumerate(examples[:5], 1):
                        if isinstance(ex, dict):
                            ex_text = ex['text']
                        else:
                            ex_text = ex
                        # Format example for readability
                        ex_formatted = ex_text.replace('\n', '\n  ')
                        f.write(f"  {i}. \"{ex_formatted}\"\n")
                
                f.write("\n" + "-" * 40 + "\n\n")
            
            f.write("\nCODING DECISION LOG\n")
            f.write("-" * 70 + "\n")
            f.write("Document any ambiguous cases and how you resolved them:\n\n")
            f.write("Case 1: [Description]\n")
            f.write("  Decision: [How resolved]\n")
            f.write("  Rationale: [Why]\n\n")
        
        print(f"✓ Codebook exported to {output_file}")
        return output_file
    
    def increment_version(self):
        """Increment rubric version (use after major revisions)"""
        current = self.metadata.get('version', 1)
        self.metadata['version'] = current + 1
        self.metadata['last_modified'] = datetime.now().isoformat()
        print(f"✓ Version incremented to {self.metadata['version']}")


def create_starter_rubric():
    """
    Create a starter rubric based on common LLM error types
    These are suggestions - modify based on your open coding!
    """
    rubric = QualitativeRubric()
    
    # Common error types for reasoning tasks
    starter_categories = {
        'LOGIC': {
            'name': 'Logical Reasoning Error',
            'definition': 'Error in logical deduction, inference, or reasoning chain. The model makes an invalid inference, contradicts itself, or fails to follow logical implications.',
            'notes': 'Look for statements like "therefore" or "thus" that don\'t logically follow from premises.'
        },
        'CALCULATION': {
            'name': 'Calculation/Computation Error',
            'definition': 'Error in mathematical calculation, arithmetic, or symbolic manipulation. The reasoning is correct but the computation is wrong.',
            'notes': 'Common in math/physics problems. Check if setup is right but execution is wrong.'
        },
        'MISUNDERSTANDING': {
            'name': 'Problem Misunderstanding',
            'definition': 'Model misinterprets the question, misses key constraints, or addresses a different problem than what was asked.',
            'notes': 'Check if the response answers a different question or ignores critical information.'
        },
        'KNOWLEDGE': {
            'name': 'Factual Knowledge Error',
            'definition': 'Model states incorrect facts, formulas, definitions, or domain-specific knowledge.',
            'notes': 'Different from reasoning errors - the model doesn\'t know or recalls incorrectly.'
        },
        'PROCEDURE': {
            'name': 'Procedural Error',
            'definition': 'Model uses wrong method, formula, or approach for the problem type. The steps don\'t match what\'s needed.',
            'notes': 'Model applies wrong framework or algorithm to solve the problem.'
        },
        'INCOMPLETE': {
            'name': 'Incomplete Reasoning',
            'definition': 'Response trails off, skips critical steps, or doesn\'t complete the solution. The reasoning chain is broken.',
            'notes': 'Look for responses that start correctly but don\'t finish or skip key steps.'
        },
        'FORMAT': {
            'name': 'Format/Expression Error',
            'definition': 'Model produces correct reasoning but fails to express the final answer in the required format (e.g., wrong option letter, unclear conclusion).',
            'notes': 'The reasoning may be correct but the final answer presentation is wrong.'
        },
        'HALLUCINATION': {
            'name': 'Hallucination/Fabrication',
            'definition': 'Model invents facts, concepts, or information not present in the problem or real knowledge.',
            'notes': 'Model makes up formulas, terms, or "facts" that don\'t exist.'
        }
    }
    
    for cat_id, cat_data in starter_categories.items():
        rubric.add_category(
            category_id=cat_id,
            name=cat_data['name'],
            definition=cat_data['definition'],
            notes=cat_data.get('notes', ''),
            examples=[]
        )
    
    rubric.metadata['created'] = datetime.now().isoformat()
    rubric.metadata['last_modified'] = datetime.now().isoformat()
    rubric.metadata['version'] = 1
    rubric.metadata['type'] = 'starter'
    
    rubric.save()
    
    print("\n" + "=" * 70)
    print("STARTER RUBRIC CREATED")
    print("=" * 70)
    print("\nThis is a STARTER rubric based on common LLM error types.")
    print("IMPORTANT: You should modify this based on your OPEN CODING!")
    print("\nNext steps:")
    print("1. Read through your error collection")
    print("2. Note patterns you observe (don\'t force into these categories)")
    print("3. Add, remove, or modify categories based on what you see")
    print("4. Add example errors to each category")
    print("5. Test the rubric on a few errors and refine")
    print("\nUse rubric.view_categories() to see current categories")
    print("Use rubric.add_category() to add new categories from your coding")
    print("Use rubric.save() to save your changes")
    
    return rubric


def interactive_rubric_builder():
    """
    Interactive tool for building rubric through open coding
    """
    print("=" * 70)
    print("INTERACTIVE RUBRIC BUILDER")
    print("=" * 70)
    print("\nThis tool helps you build a rubric through open coding.")
    print("You'll read errors and create categories based on observed patterns.\n")
    
    rubric = QualitativeRubric()
    
    if not rubric.categories:
        print("No existing rubric found. Starting fresh...")
        print("Would you like to:")
        print("1. Start with suggested categories (recommended)")
        print("2. Start from scratch")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == '1':
            return create_starter_rubric()
    
    print("\nRubric Builder Commands:")
    print("  ADD <id> <name> - Add new category")
    print("  VIEW - View all categories")
    print("  EXAMPLE <id> - Add example to category")
    print("  SAVE - Save rubric")
    print("  DONE - Finish building rubric")
    print("\nStart by reading errors and noting patterns...")
    
    return rubric


if __name__ == "__main__":
    print("=" * 70)
    print("QUALITATIVE RUBRIC DEVELOPMENT TOOL")
    print("=" * 70)
    
    # Check if rubric already exists
    rubric = QualitativeRubric()
    
    if rubric.categories:
        rubric.view_categories()
        print("\nRubric already exists. What would you like to do?")
        print("1. View categories")
        print("2. Add new category")
        print("3. Export codebook")
        print("4. Create new rubric (overwrite)")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            rubric.view_categories()
        elif choice == '2':
            cat_id = input("Category ID (e.g., LOGIC): ").strip().upper()
            name = input("Category name: ").strip()
            definition = input("Definition: ").strip()
            notes = input("Notes (optional): ").strip()
            rubric.add_category(cat_id, name, definition, notes=notes)
            rubric.save()
        elif choice == '3':
            rubric.export_codebook()
        elif choice == '4':
            create_starter_rubric()
    else:
        print("\nNo existing rubric found.")
        create_starter_rubric()
