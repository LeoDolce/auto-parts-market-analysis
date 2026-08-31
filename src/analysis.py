import os
import pandas as pd
from openpyxl.utils import get_column_letter


# ==============================================================================
# CONFIGURATION
# ==============================================================================

AUTO_PARTS_RAW_PATH = "data/raw/autopecas_capao_redondo.csv"
WORKSHOPS_RAW_PATH = "data/raw/workshops_capao_redondo.csv"
DEMOGRAPHICS_PROCESSED_PATH = "data/processed/market_research_demographics.xlsx"

FINAL_REPORT_PATH = "data/processed/final_market_research_report.xlsx"

# --------------------------------------------------------------------------
# MODELING ASSUMPTION
# --------------------------------------------------------------------------
# This is NOT an official IBGE or SENATRAN statistic.
#
# It is an analytical assumption used to estimate the vehicle population
# potentially associated with the study area's residents.
#
# The parameter is intentionally kept explicit so it can be replaced when
# better local vehicle-ownership data becomes available.
ESTIMATED_VEHICLES_PER_CAPITA = 0.33


print("Initializing Final Market Cross-Correlation Engine...")


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def load_csv_with_encoding_fallback(file_path):
    """
    Load a CSV using UTF-8 first and Latin-1 as a fallback.
    """

    try:
        return pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="latin1")


# ==============================================================================
# VALIDATE REQUIRED INPUT FILES
# ==============================================================================

if not os.path.exists(AUTO_PARTS_RAW_PATH):
    raise FileNotFoundError(
        f"[ERROR] Competitor file missing at: {AUTO_PARTS_RAW_PATH}"
    )

if not os.path.exists(WORKSHOPS_RAW_PATH):
    raise FileNotFoundError(
        f"[ERROR] Workshop file missing at: {WORKSHOPS_RAW_PATH}"
    )

if not os.path.exists(DEMOGRAPHICS_PROCESSED_PATH):
    raise FileNotFoundError(
        "[ERROR] Run the IBGE collector first. "
        f"Missing: {DEMOGRAPHICS_PROCESSED_PATH}"
    )


# ==============================================================================
# LOAD AND CLEAN COMPETITOR DATA
# ==============================================================================

print("\nLoading competitor data...")

df_autopecas = load_csv_with_encoding_fallback(AUTO_PARTS_RAW_PATH)

if "place_id" not in df_autopecas.columns:
    raise ValueError(
        "[ERROR] Competitor dataset does not contain the required 'place_id' column."
    )

# Remove duplicated Google Places records.
df_autopecas_clean = df_autopecas.drop_duplicates(
    subset=["place_id"]
).copy()

total_competitors = len(df_autopecas_clean)

print(f" -> Unique competitors: {total_competitors}")


# ==============================================================================
# LOAD AND CLEAN WORKSHOP DATA
# ==============================================================================

print("\nLoading workshop data...")

df_workshops = load_csv_with_encoding_fallback(WORKSHOPS_RAW_PATH)

if "place_id" not in df_workshops.columns:
    raise ValueError(
        "[ERROR] Workshop dataset does not contain the required 'place_id' column."
    )

# Remove duplicated Google Places records.
df_workshops_clean = df_workshops.drop_duplicates(
    subset=["place_id"]
).copy()

total_b2b_clients = len(df_workshops_clean)

print(f" -> Unique workshops: {total_b2b_clients}")


# ==============================================================================
# LOAD IBGE DEMOGRAPHIC DATA
# ==============================================================================

print("\nLoading IBGE demographic data...")

df_demo = pd.read_excel(
    DEMOGRAPHICS_PROCESSED_PATH,
    sheet_name="Demographic Indicators"
)

required_demo_columns = [
    "Allocated Population in Radius",
    "Average Monthly Income (BRL)"
]

missing_columns = [
    column
    for column in required_demo_columns
    if column not in df_demo.columns
]

if missing_columns:
    raise ValueError(
        "[ERROR] IBGE dataset is missing required columns: "
        + ", ".join(missing_columns)
    )


# ==============================================================================
# DEMOGRAPHIC AGGREGATION
# ==============================================================================

# Population allocated to the study radius based on the proportion of each
# census sector that falls inside the analyzed perimeter.

total_population = int(
    df_demo["Allocated Population in Radius"].sum()
)


# --------------------------------------------------------------------------
# POPULATION-WEIGHTED AVERAGE INCOME
# --------------------------------------------------------------------------
#
# A simple arithmetic mean would give the same importance to every census
# sector, regardless of how much population from that sector is actually
# inside the study area.
#
# Instead, each sector's income is weighted by its allocated population.
# --------------------------------------------------------------------------

df_income = df_demo[
    [
        "Allocated Population in Radius",
        "Average Monthly Income (BRL)"
    ]
].copy()

df_income = df_income.dropna(
    subset=[
        "Allocated Population in Radius",
        "Average Monthly Income (BRL)"
    ]
)

if df_income["Allocated Population in Radius"].sum() > 0:

    weighted_income = (
        (
            df_income["Allocated Population in Radius"]
            * df_income["Average Monthly Income (BRL)"]
        ).sum()
        /
        df_income["Allocated Population in Radius"].sum()
    )

else:
    weighted_income = 0


# ==============================================================================
# LOCAL FLEET ESTIMATION
# ==============================================================================

# The raw SENATRAN municipal fleet is not directly used as a local fleet
# estimate because the available geographic distribution contains major
# limitations, including a large volume of records associated with CEP
# 00000-000 and potential corporate/rental fleet distortion.
#
# Therefore, the project uses an explicit modeling assumption instead.

estimated_local_fleet = int(
    total_population * ESTIMATED_VEHICLES_PER_CAPITA
)


print("\nIngested Market Baseline:")
print(f" -> Population inside radius: {total_population:,}")
print(f" -> Weighted average income: R$ {weighted_income:,.2f}")
print(
    f" -> Estimated local fleet: {estimated_local_fleet:,}"
    f" ({ESTIMATED_VEHICLES_PER_CAPITA} vehicles/inhabitant)"
)
print(f" -> B2B target customers: {total_b2b_clients}")


# ==============================================================================
# MARKET INDICATORS
# ==============================================================================

print("\nCalculating market indicators...")


if total_competitors > 0:

    inhabitants_per_store = round(
        total_population / total_competitors
    )

    vehicles_per_store = round(
        estimated_local_fleet / total_competitors
    )

    workshops_per_store = round(
        total_b2b_clients / total_competitors,
        2
    )

else:

    inhabitants_per_store = total_population
    vehicles_per_store = estimated_local_fleet
    workshops_per_store = total_b2b_clients


# ==============================================================================
# EXECUTIVE SCORECARD
# ==============================================================================

df_market_summary = pd.DataFrame([
    {
        "Indicator Metric": "Validated Competitors (Auto Parts)",
        "Value": total_competitors,
        "Unit": "Stores"
    },
    {
        "Indicator Metric": "Target B2B Clients (Workshops)",
        "Value": total_b2b_clients,
        "Unit": "Workshops"
    },
    {
        "Indicator Metric": "Total Perimeter Population",
        "Value": total_population,
        "Unit": "Inhabitants"
    },
    {
        "Indicator Metric": "Estimated Local Fleet",
        "Value": estimated_local_fleet,
        "Unit": "Vehicles"
    },
    {
        "Indicator Metric": "Population per Competitor",
        "Value": inhabitants_per_store,
        "Unit": "Inhabitants / Store"
    },
    {
        "Indicator Metric": "Estimated Vehicles per Competitor",
        "Value": vehicles_per_store,
        "Unit": "Vehicles / Store"
    },
    {
        "Indicator Metric": "B2B Client-to-Competitor Ratio",
        "Value": workshops_per_store,
        "Unit": "Workshops / Store"
    },
    {
        "Indicator Metric": "Population-Weighted Average Income",
        "Value": round(weighted_income, 2),
        "Unit": "BRL"
    }
])


# ==============================================================================
# EXPORT CONSOLIDATED REPORT
# ==============================================================================

os.makedirs(
    os.path.dirname(FINAL_REPORT_PATH),
    exist_ok=True
)

print(
    f"\nExporting consolidated report to: "
    f"{FINAL_REPORT_PATH}"
)


with pd.ExcelWriter(
    FINAL_REPORT_PATH,
    engine="openpyxl"
) as writer:

    df_market_summary.to_excel(
        writer,
        sheet_name="Executive Scorecard",
        index=False
    )

    df_autopecas_clean.to_excel(
        writer,
        sheet_name="Cleaned Competitors",
        index=False
    )

    df_workshops_clean.to_excel(
        writer,
        sheet_name="Target B2B Clients",
        index=False
    )

    # Automatic column sizing
    for sheet_name in writer.sheets:

        worksheet = writer.sheets[sheet_name]

        for col_idx, column in enumerate(
            worksheet.columns,
            start=1
        ):

            max_len = max(
                len(str(cell.value or ""))
                for cell in column
            )

            column_letter = get_column_letter(col_idx)

            worksheet.column_dimensions[
                column_letter
            ].width = max(max_len + 4, 12)


# ==============================================================================
# TERMINAL SUMMARY
# ==============================================================================

print("\n" + "=" * 55)
print("          MARKET OPPORTUNITY BASELINE")
print("=" * 55)

print(
    f"Unique competitors:       {total_competitors}"
)

print(
    f"Target workshops:         {total_b2b_clients}"
)

print(
    f"Population in radius:     {total_population:,}"
)

print(
    f"Estimated fleet:          {estimated_local_fleet:,}"
)

print(
    f"Population / competitor:  {inhabitants_per_store:,}"
)

print(
    f"Vehicles / competitor:    {vehicles_per_store:,}"
)

print(
    f"Workshops / competitor:   {workshops_per_store}"
)

print(
    f"Weighted income:          R$ {weighted_income:,.2f}"
)

print("=" * 55)

print(
    "\nNOTE:"
    "\nThe fleet figure is an analytical estimate based on"
    f"\n{ESTIMATED_VEHICLES_PER_CAPITA} vehicles per inhabitant."
    "\nIt is not an official SENATRAN local-fleet figure."
)

print("=" * 55 + "\n")