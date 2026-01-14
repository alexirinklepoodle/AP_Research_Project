# AP Research: LLM Error Analysis Project

## Folder Structure
- `data/raw/` - Raw model responses
- `data/processed/` - Scored and analyzed data
- `problems/` - Problem sets and solutions
- `logs/` - Log files from runs
- `visualizations/` - Charts and graphs
- `backups/` - Backup files

## Scripts
1. `setup.py` - Run this first to set up folders
2. `create_problems.py` - Create problem set
3. `data_collector.py` - Main data collection script
4. `scoring_engine.py` - Score model responses
5. `analysis_tools.py` - Analyze results

## Workflow
1. Create problems in `problems/problems.csv`
2. Run `python data_collector.py` to collect data
3. Scoring happens automatically
4. Use `analysis_tools.py` for further analysis
