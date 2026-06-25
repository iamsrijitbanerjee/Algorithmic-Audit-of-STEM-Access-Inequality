import pypdf
import pandas as pd

# Structural map to decode exact, un-clubbed home states from student roll prefixes
ROLL_PREFIX_TO_STATE = {
    'AP': 'ANDHRA PRADESH', 'AS': 'ASSAM', 'AR': 'ARUNACHAL PRADESH', 'BR': 'BIHAR',
    'CH': 'CHANDIGARH', 'CG': 'CHHATTISGARH', 'DL': 'DELHI', 'GJ': 'GUJARAT',
    'HR': 'HARYANA', 'HP': 'HIMACHAL PRADESH', 'JK': 'JAMMU AND KASHMIR', 'JH': 'JHARKHAND',
    'KA': 'KARNATAKA', 'KL': 'KERALA', 'LA': 'LADAKH', 'MP': 'MADHYA PRADESH',
    'MH': 'MAHARASHTRA', 'MN': 'MANIPUR', 'ML': 'MEGHALAYA', 'MZ': 'MIZORAM',
    'NL': 'NAGALAND', 'OD': 'ODISHA', 'PB': 'PUNJAB', 'RJ': 'RAJASTHAN',
    'SK': 'SIKKIM', 'TN': 'TAMIL NADU', 'TS': 'TELANGANA', 'TR': 'TRIPURA',
    'UP': 'UTTAR PRADESH', 'UK': 'UTTARAKHAND', 'WB': 'WEST BENGAL'
}

def parse_rmo_2024_pdf(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    all_records = []
    
    for page in reader.pages:
        lines = page.extract_text().split("\n")
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 7 and parts[3] in ['M', 'F'] and parts[4].isdigit():
                roll_no = parts[2]
                prefix = roll_no[:2].upper()
                
                # Un-club states dynamically by extracting their native geographic prefix
                actual_state = ROLL_PREFIX_TO_STATE.get(prefix, "UNKNOWN")
                if actual_state != "UNKNOWN":
                    all_records.append({
                        'roll_number': roll_no,
                        'gender': parts[3],
                        'grade_standard': int(parts[4]),
                        'home_state': actual_state,
                        'is_girls_quota': 1 if parts[3] == 'F' and parts[-1] == 'B' else 0
                    })
                    
    return pd.DataFrame(all_records)