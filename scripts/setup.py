"""
Setup script for AP Research LLM project
Run this first to create all necessary folders and files
"""

import os

def setup_project():
    """Create all necessary folders and files"""
    
    print("Setting up AP Research LLM Project...")
    print("=" * 50)
    
    # Create folder structure
    folders = [
        'data/raw',
        'data/processed',
        'problems',
        'logs',
        'visualizations',
        'backups'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Created folder: {folder}")
    
    # Create README file
    readme_content = """# AP Research: LLM Error Analysis Project

## Folder Structure
- `data/raw/` - Raw model responses
- `data/processed/` - Scored and analyzed data
- `problems/` - Problem sets and solutions
- `logs/` - Log files from runs
- `visualizations/` - Charts and graphs
- `backups/` - Backup files

## Scripts
1. `setup.py` - Run this first to set up folders
2. `create_problems.py` - Create your problem set
3. `data_collector.py` - Main data collection script
4. `scoring_engine.py` - Score model responses
5. `analysis_tools.py` - Analyze results

## Workflow
1. Create problems in `problems/problems.csv`
2. Run `python data_collector.py` to collect data
3. Scoring happens automatically
4. Use `analysis_tools.py` for further analysis
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✓ Created README.md")
    
    print("\n" + "=" * 50)
    print("SETUP COMPLETE!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit/create your problems in 'problems/problems.csv'")
    print("2. Run 'python create_problems.py' to create a template")
    print("3. Run 'python data_collector.py' to start data collection")
    print("\nRemember to install required packages:")
    print("  pip install pandas matplotlib")
    
    # Create a requirements file
    with open('requirements.txt', 'w') as f:
        f.write("pandas>=1.5.0\nmatplotlib>=3.6.0\n")

if __name__ == "__main__":
    setup_project()