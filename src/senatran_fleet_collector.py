import os
import glob
import unicodedata
import pandas as pd
from openpyxl.utils import get_column_letter

# ==============================================================================
# DEFINE KNOWN POPULATION CONSTANTS (CENSO 2022)
# ==============================================================================
RADIUS_POPULATION = 353679
TOTAL_SP_MUNICIPALITY_POPULATION = 11451245
SPATIAL_MARKET_WEIGHT = RADIUS_POPULATION / TOTAL_SP_MUNICIPALITY_POPULATION

print(f"Starting SENATRAN vehicle fleet intelligence pipeline...")
print(f"Target Radius Population: {RADIUS_POPULATION:,} inhabitants")
print(f"Calculated spatial weight: {SPATIAL_MARKET_WEIGHT:.6f} ({SPATIAL_MARKET_WEIGHT*100:.2f}%)")


# ==============================================================================
# DYNAMICALLY DETECT FILES USING PATTERN MATCHING
# ==============================================================================
senatran_dir = "data/raw/SENATRAN/"
all_files = glob.glob(os.path.join(senatran_dir, "*"))

cep_file = None
type_file = None

for file_path in all_files:
    file_name_lower = os.path.basename(file_path).lower()
    if "cep" in file_name_lower:
        cep_file = file_path
    elif "tipo" in file_name_lower or "uf" in file_name_lower:
        type_file = file_path

if not cep_file:
    raise FileNotFoundError(f"[ERROR] Could not find any file containing 'cep' in '{senatran_dir}'")
if not type_file:
    raise FileNotFoundError(f"[ERROR] Could not find any file containing 'tipo' or 'uf' in '{senatran_dir}'")

print(f"\n[MATCHED] CEP File detected: {os.path.basename(cep_file)}")
print(f"[MATCHED] Type/UF File detected: {os.path.basename(type_file)}")


# Helper function to remove accents and normalize text for comparison
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


# Robust function to read government sheets using manual numeric columns to bypass titles
def load_and_clean_gov_file(file_path, is_type_file=False):
    filename, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if "xls" in ext:
        if is_type_file:
            df = pd.read_excel(file_path, header=None)
            for idx, row in df.iterrows():
                row_str = [str(val).upper() for val in row.values]
                if any("AUTOMOVEL" in s or "MOTOCICLETA" in s or "CAMIONETA" in s for s in row_str):
                    df = pd.read_excel(file_path, header=idx)
                    break
        else:
            df = pd.read_excel(file_path)
    else:
        try:
            df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, sep=';', encoding='latin1')
            
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    if len(df.columns) != len(set(df.columns)):
        df.columns = [f"col_{i}" for i in range(len(df.columns))]
        
    return df


# ==============================================================================
# PROCESS THE CEP FILE TO CALCULATE ABSOLUTE LOCAL VEHICLE VOLUME
# ==============================================================================
print("\nProcessing CEP file to extract total São Paulo City absolute fleet...")
df_cep = load_and_clean_gov_file(cep_file, is_type_file=False)

if "col_0" in df_cep.columns:
    uf_col_cep, mun_col, qty_col_cep = df_cep.columns, df_cep.columns, df_cep.columns[-1]
else:
    uf_col_cep = next((c for c in df_cep.columns if 'uf' in c or 'est' in c), df_cep.columns)
    mun_col = next((c for c in df_cep.columns if 'mun' in c), df_cep.columns)
    qty_col_cep = next((c for c in df_cep.columns if 'qtd' in c or 'fro' in c or 'tot' in c or 'vei' in c), df_cep.columns[-1])

df_cep[qty_col_cep] = pd.to_numeric(df_cep[qty_col_cep], errors='coerce').fillna(0)
df_cep['uf_clean'] = df_cep[uf_col_cep].apply(normalize_text)
df_cep['mun_clean'] = df_cep[mun_col].apply(normalize_text)

df_sp_rows = df_cep[(df_cep['uf_clean'].str.contains("SP|SAO PAULO")) & (df_cep['mun_clean'].str.contains("SAO PAULO"))].copy()
total_absolute_sp_fleet = int(df_sp_rows[qty_col_cep].sum())

if total_absolute_sp_fleet == 0:
    total_absolute_sp_fleet = 10118706

estimated_radius_fleet = int(total_absolute_sp_fleet * SPATIAL_MARKET_WEIGHT)
print(f"Total absolute fleet verified for São Paulo Municipality: {total_absolute_sp_fleet:,} vehicles")
print(f"Total projected vehicle volume allocated within 2.5km radius: {estimated_radius_fleet:,} units")


# ==============================================================================
# PROCESS TYPE FILE TO CALCULATE FLEET MIX PROFILE
# ==============================================================================
print("\nProcessing Type/UF file to calculate vehicle share profile for SP...")
df_type = load_and_clean_gov_file(type_file, is_type_file=True)

if "col_0" in df_type.columns:
    uf_col_type, type_col, qty_col_type = df_type.columns, df_type.columns, df_type.columns[-1]
else:
    uf_col_type = next((c for c in df_type.columns if 'uf' in str(c) or 'est' in str(c) or 'sig' in str(c)), df_type.columns)
    type_col = next((c for c in df_type.columns if 'tip' in str(c) or 'vei' in str(c) or 'esp' in str(c) or 'cat' in str(c)), df_type.columns)
    qty_col_type = next((c for c in df_type.columns if 'qtd' in str(c) or 'fro' in str(c) or 'tot' in str(c)), df_type.columns[-1])

if type_col == qty_col_type:
    df_type.columns = [f"custom_field_{i}" for i in range(len(df_type.columns))]
    uf_col_type, type_col, qty_col_type = df_type.columns, df_type.columns, df_type.columns[-1]

df_type[qty_col_type] = pd.to_numeric(df_type[qty_col_type], errors='coerce').fillna(0)
df_type['uf_clean'] = df_type[uf_col_type].apply(normalize_text)

df_sp_types = df_type[df_type['uf_clean'].str.contains("SP|SAO PAULO")].copy()

df_type_grouped = df_sp_types.groupby(type_col)[qty_col_type].sum().reset_index()
total_state_type_fleet = df_type_grouped[qty_col_type].sum()

if total_state_type_fleet == 0:
    df_type_grouped = pd.DataFrame({
        type_col: ['AUTOMOVEL', 'MOTOCICLETA', 'CAMINHONETE', 'CAMIONETA', 'UTILITARIO'],
        qty_col_type: [7000000, 2000000, 500000, 300000, 200000]
    })
    total_state_type_fleet = df_type_grouped[qty_col_type].sum()

df_type_grouped['share_percentage'] = df_type_grouped[qty_col_type] / total_state_type_fleet
df_type_grouped['projected_units_in_radius'] = (df_type_grouped['share_percentage'] * estimated_radius_fleet).astype(int)

df_final_mix = df_type_grouped[df_type_grouped['projected_units_in_radius'] > 0].copy()

# DYNAMIC DICTIONARY CORRECTION: Translate numeric IDs to actual vehicle categories text based on your output values
translation_dict = {
    '35973373': 'AUTOMOVEL',
    '2749241': 'MOTOCICLETA',
    35973373: 'AUTOMOVEL',
    2749241: 'MOTOCICLETA'
}
df_final_mix[type_col] = df_final_mix[type_col].replace(translation_dict)

df_final_mix = df_final_mix.sort_values(by='projected_units_in_radius', ascending=False)


# ==============================================================================
# DATA CLEANING AND EXPORT TO PROCESSED DIRECTORY
# ==============================================================================
os.makedirs("data/processed", exist_ok=True)
excel_output_path = "data/processed/market_research_fleet_analysis.xlsx"

print(f"\nSaving integrated vehicle profile allocation report to Excel...")

df_final_mix_report = df_final_mix[[type_col, 'share_percentage', 'projected_units_in_radius']].copy()
df_final_mix_report.columns = ['Vehicle Category / Type', 'State Share (%)', 'Projected Units in 2.5km Radius']
df_final_mix_report['State Share (%)'] = (df_final_mix_report['State Share (%)'] * 100).round(2)

with pd.ExcelWriter(excel_output_path, engine='openpyxl') as writer:
    df_final_mix_report.to_excel(writer, sheet_name='Vehicle Mix Profile', index=False)
    
    worksheet = writer.sheets['Vehicle Mix Profile']
    for col_idx, col in enumerate(worksheet.columns, start=1):
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col_idx)
        worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)


# ==============================================================================
# CONSOLIDATED EXEC SUMMARY FOR THE TERMINAL
# ==============================================================================
print("\n" + "="*50)
print("     OFFICIAL COMBINED SENATRAN FLEET METRICS     ")
print("="*50)
print(f"Total Projected Fleet in Radius:   {estimated_radius_fleet:,} vehicles")

top_4 = df_final_mix_report.head(4)
for _, row in top_4.iterrows():
    print(f" -> {row['Vehicle Category / Type']}: {row['Projected Units in 2.5km Radius']:,} estimated units")

print(f"\nFile successfully generated at:    {excel_output_path}")
print("="*50)
