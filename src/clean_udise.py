import pandas as pd
import numpy as np

def clean_udise_spreadsheet(file_path):
    """
    Ingests raw district-level UDISE+ data, normalizes string keys, 
    and extracts the targeted independent socioeconomic indicators.
    """
    # Read Excel or CSV; skiprows helps bypass decorative government titles
    df = pd.read_excel(file_path, skiprows=3)
    
    # Standardize column labels to lowercase snake_case
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')
    
    # Safety check: Ensure standard geographic columns exist
    if 'state_name' not in df.columns or 'district_name' not in df.columns:
        raise ValueError("Missing state_name or district_name columns in the source spreadsheet.")
        
    # Clean the geographic text formatting to prevent string matching issues
    df['state_clean'] = df['state_name'].astype(str).str.strip().str.upper().ffill()
    df['district_clean'] = df['district_name'].astype(str).str.strip().str.upper()
    
    # Drop row entries that act as totals or national summaries rather than districts
    df = df.dropna(subset=['district_name'])
    df = df[~df['district_clean'].str.contains('TOTAL|SUMMARY', na=False)]
    
    # Define our targeted core numeric columns
    target_columns = {
        'pupil_teacher_ratio': 'ptr_secondary',
        'percent_electricity': 'pct_electricity',
        'percent_internet': 'pct_internet',
        'school_location_type': 'urban_rural_ratio'
    }
    
    # Safely convert target columns to float representations, removing formatting characters
    for raw_col, clean_col in target_columns.items():
        if raw_col in df.columns:
            df[clean_col] = pd.to_numeric(
                df[raw_col].astype(str).str.replace('%', '').str.replace(r'[^\d.]', '', regex=True), 
                errors='coerce'
            )
        else:
            # Fallback if a specific sub-metric needs to be imputed
            df[clean_col] = np.nan

    # Return a tight matrix focusing on our chosen independent features
    output_cols = ['state_clean', 'district_clean', 'ptr_secondary', 'pct_electricity', 'pct_internet']
    return df[output_cols].reset_index(drop=True)

print("UDISE+ Cleaning Module Successfully Initialized.")