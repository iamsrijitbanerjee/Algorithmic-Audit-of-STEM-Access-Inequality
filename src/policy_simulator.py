import pandas as pd
import numpy as np
import os

def run_policy_intervention_simulation():
    matrix_path = "data/processed/master_stem_matrix.csv"
    df = pd.read_csv(matrix_path)
    
    print("\n" + "="*75)
    print("🏛️ POLICY INFRASTRUCTURE INTERVENTION SIMULATOR")
    print("="*75)
    
    target_state = input("Enter State name to run simulation: ").upper().strip()
    matched = df[df['region_name'].str.contains(target_state, na=False, case=False)]
    if matched.empty:
        return
        
    state_row = matched.iloc[0]
    current_score = float(state_row['avg_state_qualification_score'])
    current_labs = float(state_row['science_lab_pct'])
    current_smart = float(state_row['smart_class_pct'])
    current_ptr = float(state_row['pupil_teacher_ratio'])
    
    new_labs = float(input(f" -> Proposed Science Lab % (Current {current_labs:.1f}%): ") or current_labs)
    new_smart = float(input(f" -> Proposed Smart TV % (Current {current_smart:.1f}%): ") or current_smart)
    new_ptr = float(input(f" -> Proposed Pupil-Teacher Ratio (Current {current_ptr:.1f}): ") or current_ptr)
    
    delta_labs = (new_labs - current_labs) * 0.125
    delta_smart = (new_smart - current_smart) * 0.165
    delta_ptr = (current_ptr - new_ptr) * 0.025
    
    simulated_score = max(0.0, current_score + (current_score * ((delta_labs + delta_smart + delta_ptr) / 100.0)))
    
    print("\n" + "="*75)
    print(f" 🚀 PROJECTED POST-INTERVENTION WEIGHT FOR {state_row['region_name']}: {simulated_score:.4f}")
    print("="*75 + "\n")

if __name__ == "__main__":
    run_policy_intervention_simulation()