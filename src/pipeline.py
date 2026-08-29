import subprocess
import sys

print("==================================================")
# BAR FORMATTER EXTENSION COMPLIANCE
print("   AUTO PARTS MARKET ANALYSIS - MASTER PIPELINE   ")
print("==================================================\n")

def run_script(script_name):
    """Executes a python script submodule as a pipeline step."""
    print(f"[RUNNING STEP] -> {script_name}")
    try:
        # Executes the script using the same python interpreter active env
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"[SUCCESS] Step {script_name} completed seamlessly.\n")
    except subprocess.CalledProcessError as e:
        print(f"\n[CRITICAL ERROR] Pipeline broke during step: {script_name}")
        print(f"Exit code: {e.returncode}")
        sys.exit(1)

# ==============================================================================
# SEQUENTIAL EXECUTION WORKFLOW ORDER
# ==============================================================================

# Step 1: Clean previous run data data outputs
run_script("src/cleaner.py")

# Step 2: Fetch Competitors and B2B Clients via Google Places API
run_script("src/google_places_collector.py")
run_script("src/google_workshops_collector.py")

# Step 3: Run IBGE 2022 Census demographic spatial queries
run_script("src/ibge_demographics_collector.py")

# Step 4: Run SENATRAN 2026 fleet data processing allocation
run_script("src/senatran_fleet_collector.py")

# Step 5: Execute final data correlation and scoring metrics
run_script("src/analysis.py")

print("==================================================")
print("  MASTER PIPELINE EXECUTION COMPLETED WITH SUCCESS ")
print("==================================================")
