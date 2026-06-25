import pandas as pd
import numpy as np
import os
from scipy import stats

STATE_ADJACENCY_MAP = {
    'ANDHRA PRADESH': ['TELANGANA', 'KARNATAKA', 'TAMIL NADU', 'ODISHA', 'CHHATTISGARH'],
    'ARUNACHAL PRADESH': ['ASSAM', 'NAGALAND'],
    'ASSAM': ['ARUNACHAL PRADESH', 'NAGALAND', 'MANIPUR', 'MIZORAM', 'TRIPURA', 'MEGHALAYA', 'WEST BENGAL'],
    'BIHAR': ['UTTAR PRADESH', 'JHARKHAND', 'WEST BENGAL'],
    'CHANDIGARH': ['PUNJAB', 'HARYANA'],
    'CHHATTISGARH': ['MADHYA PRADESH', 'MAHARASHTRA', 'ANDHRA PRADESH', 'TELANGANA', 'ODISHA', 'JHARKHAND', 'UTTAR PRADESH'],
    'DELHI': ['HARYANA', 'UTTAR PRADESH'],
    'GOA': ['MAHARASHTRA', 'KARNATAKA'],
    'GUJARAT': ['RAJASTHAN', 'MADHYA PRADESH', 'MAHARASHTRA'],
    'HARYANA': ['PUNJAB', 'HIMACHAL PRADESH', 'RAJASTHAN', 'UTTAR PRADESH', 'DELHI', 'CHANDIGARH'],
    'HIMACHAL PRADESH': ['JAMMU AND KASHMIR', 'LADAKH', 'PUNJAB', 'HARYANA', 'UTTARAKHAND'],
    'JAMMU AND KASHMIR': ['LADAKH', 'HIMACHAL PRADESH', 'PUNJAB'],
    'JHARKHAND': ['BIHAR', 'WEST BENGAL', 'ODISHA', 'CHHATTISGARH', 'UTTAR PRADESH'],
    'KARNATAKA': ['GOA', 'MAHARASHTRA', 'TELANGANA', 'ANDHRA PRADESH', 'TAMIL NADU', 'KERALA'],
    'KERALA': ['KARNATAKA', 'TAMIL NADU'],
    'LADAKH': ['JAMMU AND KASHMIR', 'HIMACHAL PRADESH'],
    'MADHYA PRADESH': ['RAJASTHAN', 'UTTAR PRADESH', 'CHHATTISGARH', 'MAHARASHTRA', 'GUJARAT'],
    'MAHARASHTRA': ['GUJARAT', 'MADHYA PRADESH', 'CHHATTISGARH', 'TELANGANA', 'KARNATAKA', 'GOA'],
    'MANIPUR': ['NAGALAND', 'ASSAM', 'MIZORAM'],
    'MEGHALAYA': ['ASSAM'],
    'MIZORAM': ['TRIPURA', 'ASSAM', 'MANIPUR'],
    'NAGALAND': ['ARUNACHAL PRADESH', 'ASSAM', 'MANIPUR'],
    'ODISHA': ['WEST BENGAL', 'JHARKHAND', 'CHHATTISGARH', 'ANDHRA PRADESH'],
    'PUNJAB': ['JAMMU AND KASHMIR', 'HIMACHAL PRADESH', 'HARYANA', 'RAJASTHAN', 'CHANDIGARH'],
    'RAJASTHAN': ['PUNJAB', 'HARYANA', 'UTTAR PRADESH', 'MADHYA PRADESH', 'GUJARAT'],
    'SIKKIM': ['WEST BENGAL'],
    'TAMIL NADU': ['KERALA', 'KARNATAKA', 'ANDHRA PRADESH'],
    'TELANGANA': ['MAHARASHTRA', 'CHHATTISGARH', 'KARNATAKA', 'ANDHRA PRADESH'],
    'TRIPURA': ['ASSAM', 'MIZORAM'],
    'UTTAR PRADESH': ['UTTARAKHAND', 'HARYANA', 'DELHI', 'RAJASTHAN', 'MADHYA PRADESH', 'CHHATTISGARH', 'JHARKHAND', 'BIHAR'],
    'UTTARAKHAND': ['HIMACHAL PRADESH', 'UTTAR PRADESH'],
    'WEST BENGAL': ['SIKKIM', 'ASSAM', 'BIHAR', 'JHARKHAND', 'ODISHA']
}

def compute_global_morans_i():
    matrix_path = "data/processed/master_stem_matrix.csv"
    if not os.path.exists(matrix_path):
        return
    df = pd.read_csv(matrix_path)
    print("\n--- [STAGE 4] Running High-Fidelity Spatial Auto-Correlation Matrix Analysis ---")
    
    states_in_data = df['region_name'].tolist()
    y = df['avg_state_qualification_score'].values
    y_deviation = y - np.mean(y)
    N = len(df)
    
    W = np.zeros((N, N))
    for i, state_i in enumerate(states_in_data):
        neighbors = STATE_ADJACENCY_MAP.get(state_i, [])
        for neighbor in neighbors:
            if neighbor in states_in_data:
                W[i, states_in_data.index(neighbor)] = 1.0
        row_sum = np.sum(W[i, :])
        if row_sum > 0:
            W[i, :] = W[i, :] / row_sum
            
    W_0 = np.sum(W)
    numerator = sum(W[i, j] * y_deviation[i] * y_deviation[j] for i in range(N) for j in range(N))
    denominator = np.sum(y_deviation ** 2)
    morans_i = (N / W_0) * (numerator / denominator)
    
    print(f" -> Computed Global Moran's I Value Spatial Vector: {morans_i:.4f}")

if __name__ == "__main__":
    compute_global_morans_i()