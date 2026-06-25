import os

def build_longitudinal_directory_vault():
    print("--- [INITIALIZING] Setting Up Longitudinal Panel & UDISE Vaults ---")
    
    # 1. Generate Olympiad Time-Series Folders (2011 to 2025)
    target_years = [str(year) for year in range(2011, 2026)]
    disciplines = ['mathematics', 'physics', 'chemistry', 'informatics', 'biology']
    base_raw_olympiad = "data/raw_olympiad"
    
    olympiad_counter = 0
    for year in target_years:
        for discipline in disciplines:
            nested_path = os.path.join(base_raw_olympiad, year, discipline)
            if not os.path.exists(nested_path):
                os.makedirs(nested_path, exist_ok=True)
                olympiad_counter += 1

    # 2. Generate Annual UDISE+ Demographic Folders
    # Maps corresponding academic cycles: 2023-24 -> '2023_24'
    udise_cycles = [f"{year}_{str(year+1)[2:]}" for year in range(2011, 2025)]
    base_raw_udise = "data/raw_udise"
    
    udise_counter = 0
    for cycle in udise_cycles:
        nested_udise_path = os.path.join(base_raw_udise, cycle)
        if not os.path.exists(nested_udise_path):
            os.makedirs(nested_udise_path, exist_ok=True)
            udise_counter += 1
                
    os.makedirs("data/processed", exist_ok=True)
    
    print(f"STATUS: Verified/Created {olympiad_counter} Olympiad subfolders.")
    print(f"STATUS: Verified/Created {udise_counter} UDISE+ annual subfolders.")
    print("🚀 System directory maps ready for historical files.")

if __name__ == "__main__":
    build_longitudinal_directory_vault()