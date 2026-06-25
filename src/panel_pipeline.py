import os
import pandas as pd
import glob

def run_multidimensional_panel_compiler():
    print("\n" + "="*80)
    print("🚀 COMPILING NATIONAL POLY-OLYMPIAD TIME-SERIES LONGITUDINAL PANEL TENSOR")
    print("="*80)
    
    base_raw_path = "data/raw_olympiad"
    panel_records = []
    
    if not os.path.exists(base_raw_path):
        return

    for year_folder in sorted(os.listdir(base_raw_path)):
        year_path = os.path.join(base_raw_path, year_folder)
        if not os.path.isdir(year_path): 
            continue 
            
        for discipline in os.listdir(year_path):
            discipline_path = os.path.join(year_path, discipline)
            if not os.path.isdir(discipline_path): 
                continue
                
            # Dynamically ingest any stage qualifiers table discovered across the historical matrix
            search_pattern = os.path.join(discipline_path, "stage*_qualifiers.csv")
            discovered_stages = glob.glob(search_pattern)
            
            for stage_csv in discovered_stages:
                print(f" ✅ HARVESTING PANEL ENTRY: [{year_folder}] | Subj [{discipline}] | File [{os.path.basename(stage_csv)}]")
                df_year = pd.read_csv(stage_csv)
                df_year['year_timestamp'] = int(year_folder)
                df_year['olympiad_type'] = discipline
                df_year['stage_tier_origin'] = os.path.basename(stage_csv).split('_')[0]
                panel_records.append(df_year)

    output_panel_path = "data/processed/master_panel_tensor.csv"
    if panel_records:
        pd.concat(panel_records, ignore_index=True).to_csv(output_panel_path, index=False)
        print(f"🎉 SUCCESS: Multi-stage longitudinal panel compiled at: {output_panel_path}")
    else:
        print(" ℹ️ Monitoring loops active. Awaiting historical poly-stage CSV uploads.")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_multidimensional_panel_compiler()