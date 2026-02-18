"""
Qualitative Coding Interface

This script provides an interface for applying the qualitative rubric to errors:
1. Load error collection and rubric
2. Code each error for primary and secondary error types
3. Document coding decisions and ambiguous cases
4. Export coded data for reliability analysis

Usage:
    python3 scripts/qualitative_coding.py
    
    Or for batch coding with existing rubric:
    python3 scripts/qualitative_coding.py --batch --input <error_file> --output <coded_file>
"""

import csv
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class QualitativeCoder:
    """Interface for applying qualitative rubric to errors"""
    
    def __init__(self, error_file: str = None, rubric_file: str = None):
        self.errors = []
        self.rubric = {}
        self.coded_errors = []
        self.ambiguous_cases = []
        
        # Load rubric
        if rubric_file is None:
            rubric_files = glob.glob('data/processed/rubric.json')
            rubric_file = rubric_files[0] if rubric_files else None
        
        if rubric_file:
            self.load_rubric(rubric_file)
        else:
            print("⚠ No rubric found. Run qualitative_rubric.py first.")
        
        # Load errors
        if error_file is None:
            error_files = glob.glob('data/processed/error_collection_coding_*.csv')
            error_file = max(error_files) if error_files else None
        
        if error_file:
            self.load_errors(error_file)
        else:
            print("⚠ No error collection found. Run error_collection.py first.")
    
    def load_rubric(self, rubric_file: str):
        """Load coding rubric"""
        with open(rubric_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.rubric = data.get('categories', {})
        print(f"✓ Loaded rubric with {len(self.rubric)} categories")
    
    def load_errors(self, error_file: str):
        """Load error collection"""
        with open(error_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.errors = list(reader)
        print(f"✓ Loaded {len(self.errors)} errors to code")
        print(f"  Source: {error_file}")
    
    def display_error(self, error: Dict, show_full: bool = False) -> str:
        """Format error for display during coding"""
        output = []
        output.append("=" * 70)
        output.append(f"ERROR ID: {error.get('error_id', 'N/A')}")
        output.append(f"Model: {error.get('model_name', 'N/A')} ({error.get('model_group', 'N/A')})")
        output.append(f"Problem Type: {error.get('problem_type', 'N/A')}")
        output.append("-" * 70)
        
        # Problem text (truncated if too long)
        problem_text = error.get('problem_text', '')
        if len(problem_text) > 800 and not show_full:
            problem_text = problem_text[:800] + "... [truncated]"
        output.append("PROBLEM:")
        output.append(problem_text)
        output.append("-" * 70)
        
        # Model response
        response = error.get('model_response', error.get('response', ''))
        if len(response) > 1000 and not show_full:
            response = response[:1000] + "... [truncated]"
        output.append("MODEL RESPONSE:")
        output.append(response)
        output.append("-" * 70)
        
        # Correct solution
        output.append("CORRECT SOLUTION:")
        output.append(error.get('correct_solution', 'N/A'))
        output.append("-" * 70)
        
        # Extracted answer
        output.append(f"Model's Final Answer: {error.get('extracted_answer', 'N/A')}")
        output.append("=" * 70)
        
        return '\n'.join(output)
    
    def display_rubric(self) -> str:
        """Display current rubric categories"""
        output = []
        output.append("\nCODING RUBRIC")
        output.append("-" * 70)
        
        for cat_id, cat_data in sorted(self.rubric.items()):
            name = cat_data.get('name', cat_id)
            output.append(f"[{cat_id}] {name}")
        
        output.append("-" * 70)
        output.append("Enter category ID for primary error, or 'SKIP' to skip")
        return '\n'.join(output)
    
    def code_error(self, error: Dict, primary: str = None, secondary: str = None,
                   confidence: str = None, notes: str = "") -> Dict:
        """
        Code a single error
        
        Args:
            error: Error dictionary
            primary: Primary error type (category ID)
            secondary: Secondary error type (optional)
            confidence: Confidence level (high/medium/low)
            notes: Coder notes
        
        Returns:
            Updated error dictionary with coding
        """
        coded = error.copy()
        coded['primary_error_type'] = primary or ''
        coded['secondary_error_type'] = secondary or ''
        coded['confidence'] = confidence or ''
        coded['coder_notes'] = notes or ''
        coded['coded_date'] = datetime.now().isoformat()
        
        return coded
    
    def code_all_interactive(self, start_idx: int = 0):
        """
        Interactive coding session
        
        Args:
            start_idx: Index to start coding from
        """
        print("\n" + "=" * 70)
        print("QUALITATIVE CODING SESSION")
        print("=" * 70)
        print(f"Total errors to code: {len(self.errors)}")
        print(f"Starting at error {start_idx + 1}")
        print("\nCommands:")
        print("  <category_id> [secondary] [confidence] - Code error")
        print("  SHOW - Show full error text")
        print("  RUBRIC - Show rubric")
        print("  NOTES - Add notes")
        print("  SKIP - Skip this error")
        print("  QUIT - Save and quit")
        print("=" * 70)
        
        coded_count = 0
        skip_count = 0
        
        for i, error in enumerate(self.errors[start_idx:], start=start_idx):
            print(f"\nError {i + 1}/{len(self.errors)}")
            print(self.display_error(error))
            print(self.display_rubric())
            
            while True:
                user_input = input("\nCoding: ").strip()
                
                if user_input.upper() == 'QUIT':
                    print(f"\n✓ Saved {coded_count} coded errors")
                    print(f"  Skipped {skip_count} errors")
                    self.save_progress()
                    return
                
                if user_input.upper() == 'SHOW':
                    print(self.display_error(error, show_full=True))
                    continue
                
                if user_input.upper() == 'RUBRIC':
                    print(self.display_rubric())
                    continue
                
                if user_input.upper() == 'SKIP':
                    skip_count += 1
                    print("  → Skipped")
                    break
                
                if user_input.upper() == 'NOTES':
                    notes = input("Enter notes: ").strip()
                    error['coder_notes'] = notes
                    continue
                
                # Parse coding input
                parts = user_input.split()
                primary = parts[0].upper() if parts else ''
                secondary = parts[1].upper() if len(parts) > 1 else ''
                confidence = parts[2].lower() if len(parts) > 2 else 'medium'
                
                # Validate primary category
                if primary and primary not in self.rubric:
                    print(f"  ✗ Invalid category: {primary}")
                    print(f"  Valid categories: {', '.join(self.rubric.keys())}")
                    continue
                
                # Validate secondary category
                if secondary and secondary not in self.rubric:
                    print(f"  ✗ Invalid secondary category: {secondary}")
                    continue
                
                # Code the error
                notes = error.get('coder_notes', '')
                coded = self.code_error(error, primary, secondary, confidence, notes)
                self.coded_errors.append(coded)
                coded_count += 1
                
                cat_name = self.rubric[primary].get('name', primary)
                print(f"  → Coded: {cat_name}" + 
                      (f" + {secondary}" if secondary else "") +
                      f" ({confidence})")
                break
        
        print(f"\n✓ Session complete!")
        print(f"  Coded: {coded_count} errors")
        print(f"  Skipped: {skip_count} errors")
        self.save_progress()
    
    def code_error_batch(self, error: Dict, rubric: Dict) -> Dict:
        """
        Apply rubric to a single error (for batch processing)
        This is a placeholder - you would implement automated coding here
        or use it for semi-automated coding with LLM assistance
        """
        # For now, mark as uncoded
        return self.code_error(error, '', '', '', 'Requires manual coding')
    
    def save_progress(self, output_file: str = None):
        """Save coding progress"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'data/processed/coded_errors_{timestamp}.csv'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        if not self.coded_errors:
            print("⚠ No coded errors to save")
            return None
        
        # Define fieldnames
        fieldnames = list(self.coded_errors[0].keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.coded_errors)
        
        print(f"✓ Saved {len(self.coded_errors)} coded errors to {output_file}")
        return output_file
    
    def load_progress(self, progress_file: str):
        """Load previous coding progress"""
        with open(progress_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.coded_errors = list(reader)
        print(f"✓ Loaded {len(self.coded_errors)} previously coded errors")
    
    def get_coding_summary(self) -> Dict:
        """Get summary of coding progress"""
        from collections import Counter
        
        total = len(self.errors)
        coded = len(self.coded_errors)
        remaining = total - coded
        
        # Category distribution
        primary_counts = Counter(e.get('primary_error_type', '') for e in self.coded_errors)
        secondary_counts = Counter(
            e.get('secondary_error_type', '') 
            for e in self.coded_errors 
            if e.get('secondary_error_type')
        )
        
        # Confidence distribution
        confidence_counts = Counter(e.get('confidence', '') for e in self.coded_errors)
        
        return {
            'total_errors': total,
            'coded': coded,
            'remaining': remaining,
            'percent_complete': (coded / total * 100) if total > 0 else 0,
            'primary_distribution': dict(primary_counts),
            'secondary_distribution': dict(secondary_counts),
            'confidence_distribution': dict(confidence_counts)
        }
    
    def print_summary(self):
        """Print coding summary"""
        summary = self.get_coding_summary()
        
        print("\n" + "=" * 70)
        print("CODING PROGRESS")
        print("=" * 70)
        print(f"Total errors: {summary['total_errors']}")
        print(f"Coded: {summary['coded']} ({summary['percent_complete']:.1f}%)")
        print(f"Remaining: {summary['remaining']}")
        
        if summary['primary_distribution']:
            print("\nPrimary Error Types:")
            for cat, count in sorted(summary['primary_distribution'].items(), 
                                     key=lambda x: -x[1]):
                if cat:  # Skip empty
                    pct = count / summary['coded'] * 100
                    print(f"  {cat}: {count} ({pct:.1f}%)")
        
        if summary['confidence_distribution']:
            print("\nConfidence Distribution:")
            for conf, count in sorted(summary['confidence_distribution'].items()):
                if conf:  # Skip empty
                    pct = count / summary['coded'] * 100
                    print(f"  {conf}: {count} ({pct:.1f}%)")
        
        print("=" * 70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Qualitative Coding Interface')
    parser.add_argument('--batch', action='store_true', help='Batch mode')
    parser.add_argument('--input', type=str, help='Input error file')
    parser.add_argument('--output', type=str, help='Output coded file')
    parser.add_argument('--resume', type=str, help='Resume from progress file')
    parser.add_argument('--start', type=int, default=0, help='Start index')
    
    args = parser.parse_args()
    
    # Initialize coder
    coder = QualitativeCoder(error_file=args.input)
    
    if args.resume:
        coder.load_progress(args.resume)
    
    if args.batch:
        print("Batch mode not yet implemented. Use interactive mode.")
        return
    
    # Interactive mode
    if coder.errors:
        coder.code_all_interactive(start_idx=args.start)
        coder.print_summary()
    else:
        print("No errors loaded. Please provide an error collection file.")


if __name__ == "__main__":
    main()
