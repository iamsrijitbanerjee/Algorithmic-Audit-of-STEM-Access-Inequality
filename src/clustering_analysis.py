import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def execute_unsupervised_segmentation():
    matrix_path = "data/processed/master_stem_matrix.csv"
    if not os.path.exists(matrix_path):
        return
        
    df = pd.read_csv(matrix_path)
    print("\n--- [STAGE 2] Running Unsupervised Typology Clustering Architecture ---")
    
    features = [
        'pupil_teacher_ratio', 'science_lab_pct', 'internet_access_pct',
        'gender_parity_index', 'literacy_proxy_ger', 'electricity_pct',
        'toilets_pct', 'computers_pct', 'smart_class_pct', 'avg_teachers_per_school'
    ]
    
    X = df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=3, init='k-means++', max_iter=300, random_state=42)
    df['cluster_archetype_id'] = kmeans.fit_predict(X_scaled)
    
    df.to_csv(matrix_path, index=False)
    print(" ✅ Macro-structural archetype profiles successfully fused to matrix.")

if __name__ == "__main__":
    execute_unsupervised_segmentation()