import pandas as pd
import os

def run_console_input_simulator():
    matrix_path = "data/processed/master_stem_matrix.csv"
    if not os.path.exists(matrix_path):
        return
    df = pd.read_csv(matrix_path)
    
    print("\n" + "="*75)
    print("🚀 INDIVIDUAL MULTI-STAGE EDGE BAYESIAN PROBABILITY SIMULATOR")
    print("="*75)
    
    input_state = input("Enter Target Region Zone: ").upper().strip()
    input_stage = int(input("Enter Competitive Tier Level Stage (1 to N): "))
    input_pathway = input("Enter Pathway Classification Model (MAS/MI): ").upper().strip()
    input_class = int(input("Enter Academic Standard Grade (8-12): "))
    
    matched = df[df['region_name'].str.contains(input_state, na=False, case=False)]
    row = matched.iloc[0] if not matched.empty else df.mean(numeric_only=True)
    
    # Mathematical progression arrays matched natively to structural definitions
    w_stage = 3.5 ** (input_stage - 1)
    alpha = 1.25 if input_pathway == "MAS" else 1.00
    gamma = {8: 2.50, 9: 2.50, 10: 1.75, 11: 1.25, 12: 1.00}.get(input_class, 1.00)
    
    final_custom_score = float(row['avg_state_qualification_score']) * w_stage * alpha * gamma
    print(f"\n 🎯 INDIVIDUAL APTITUDE CAPABILITY INDEX VALUE: {final_custom_score:.4f}\n")

if __name__ == "__main__":
    run_console_input_simulator()