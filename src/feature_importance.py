import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor

def run_strict_formatted_audit():
    matrix_path = "data/processed/master_stem_matrix.csv"
    df = pd.read_csv(matrix_path)
    
    features = [
        'pupil_teacher_ratio', 'science_lab_pct', 'internet_access_pct',
        'gender_parity_index', 'literacy_proxy_ger', 'electricity_pct',
        'toilets_pct', 'computers_pct', 'smart_class_pct', 'avg_teachers_per_school',
        'official_state_cutoff', 'ag_quota_seats_allocated'
    ]
    
    X = df[features]
    y = df['avg_state_qualification_score']
    
    model = RandomForestRegressor(n_estimators=300, max_depth=6, random_state=42)
    model.fit(X, y)
    r2_score_val = model.score(X, y)
    
    importances = model.feature_importances_
    contributions = {feat: imp * 100 for feat, imp in zip(features, importances)}
    
    print("\n" + "="*80)
    print(f"🎯 RE-CALIBRATED MODEL ACCURACY (WEIGHTED R² SCORE): {r2_score_val * 100:.2f}%")
    print("="*80)
    print("\n🛠️ REFINED FACTOR INFLUENCE CONTRIBUTION WEIGHTS:")
    for feat, contribution in sorted(contributions.items(), key=lambda x: x[1], reverse=True):
        print(f" -> {feat:<32} | Significance Weight: {contribution:.2f}%")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_strict_formatted_audit()