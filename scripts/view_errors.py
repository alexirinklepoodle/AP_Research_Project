"""Display sample errors for open coding review"""
import pandas as pd

df = pd.read_csv('data/processed/error_collection_coding_20260217_205141.csv')

print('=' * 80)
print('SAMPLE ERRORS FOR OPEN CODING')
print('=' * 80)
print(f'Total errors to review: {len(df)}\n')

for idx, row in df.head(5).iterrows():
    print('\n' + '=' * 80)
    print(f"ERROR {row['error_id']} | Model: {row['model_name']} ({row['model_group']})")
    print(f"Type: {row['problem_type']}")
    print('-' * 80)
    print('PROBLEM:')
    problem_text = row['problem_text']
    print(problem_text[:400] + '...' if len(str(problem_text)) > 400 else problem_text)
    print('-' * 80)
    print('MODEL RESPONSE:')
    response = row['model_response']
    print(response[:500] + '...' if len(str(response)) > 500 else response)
    print('-' * 80)
    print('CORRECT SOLUTION:')
    print(row['correct_solution'])
    print('-' * 80)
    print("MODEL'S FINAL ANSWER:")
    print(row['extracted_answer'])

print('\n' + '=' * 80)
print('END OF SAMPLE')
print('=' * 80)
