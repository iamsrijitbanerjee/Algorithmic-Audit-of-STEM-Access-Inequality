import pandas as pd
import numpy as np
import os
from spatial_analysis import STATE_ADJACENCY_MAP

def run_geospatial_gnn_engine():
    matrix_path = "data/processed/master_stem_matrix.csv"
    df = pd.read_csv(matrix_path)
    print("\n--- [STAGE 5] Isolating System STEM Access Deserts via Topological GNN Layer ---")
    
    states = df['region_name'].tolist()
    y = df['avg_state_qualification_score'].values
    N = len(df)
    
    feature_cols = [
        'pupil_teacher_ratio', 'science_lab_pct', 'internet_access_pct',
        'gender_parity_index', 'literacy_proxy_ger', 'electricity_pct',
        'toilets_pct', 'computers_pct', 'smart_class_pct', 'avg_teachers_per_school'
    ]
    X = df[feature_cols].values
    X_norm = (X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-5)
    
    A = np.zeros((N, N))
    for i, state_i in enumerate(states):
        neighbors = STATE_ADJACENCY_MAP.get(state_i, [])
        for neighbor in neighbors:
            if neighbor in states:
                A[i, states.index(neighbor)] = 1.0
                
    A_hat = A + np.eye(N)
    degrees = np.sum(A_hat, axis=1)
    D_inv_sqrt = np.diag(1.0 / np.sqrt(degrees))
    A_normalized = np.dot(np.dot(D_inv_sqrt, A_hat), D_inv_sqrt)
    
    H_layer1 = np.dot(A_normalized, X_norm)
    capacity_index = np.mean(H_layer1, axis=1)
    
    predicted_yield = (capacity_index - np.min(capacity_index)) / (np.max(capacity_index) - np.min(capacity_index) + 1e-5)
    predicted_yield = predicted_yield * np.max(y)
    
    df['expected_stem_capacity'] = predicted_yield
    df['stem_desert_score'] = df['expected_stem_capacity'] - df['avg_state_qualification_score']
    
    print("\n" + "="*80)
    print("🎯 RE-CALIBRATED GRAPH NEURAL NETWORK TARGET INDEX:")
    deserts_df = df.sort_values(by='stem_desert_score', ascending=False)
    for _, row in deserts_df.head(3).iterrows():
        print(f"  -> {row['region_name']:<25} | Desert Disparity Score: +{row['stem_desert_score']:.4f}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_geospatial_gnn_engine()