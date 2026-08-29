import os
import glob

print("Starting pipeline cleaning engine...")

# Define paths to clear before a new run
files_to_delete = [
    "data/raw/autopecas_capao_redondo.csv",
    "data/raw/oficinas_capao_redondo.csv",
    "data/processed/market_research_demographics.xlsx",
    "data/processed/market_research_fleet_analysis.xlsx",
    "data/processed/final_market_research_report.xlsx"
]

deleted_count = 0
for file_path in files_to_delete:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f" -> Deleted old execution file: {file_path}")
        deleted_count += 1

if deleted_count == 0:
    print(" -> No old execution files found. Workspace is already clean.")
else:
    print(f" -> Workspace clean up completed. {deleted_count} files removed.")
print("="*50)
