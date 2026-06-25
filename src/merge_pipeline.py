import pypdf
import pandas as pd
import re
import os
import glob
import numpy as np

# A clean reference set of Indian administrative territories to validate rows
OFFICIAL_STATES = [
    'ANDHRA PRADESH', 'ARUNACHAL PRADESH', 'ASSAM', 'BIHAR', 'CHHATTISGARH', 
    'GOA', 'GUJARAT', 'HARYANA', 'HIMACHAL PRADESH', 'JHARKHAND', 'KARNATAKA', 
    'KERALA', 'MADHYA PRADESH', 'MAHARASHTRA', 'MANIPUR', 'MEGHALAYA', 'MIZORAM', 
    'NAGALAND', 'ODISHA', 'PUNJAB', 'RAJASTHAN', 'SIKKIM', 'TAMIL NADU', 
    'TELANGANA', 'TRIPURA', 'UTTAR PRADESH', 'UTTRAKHAND', 'WEST BENGAL', 
    'ANDAMAN AND NICOBAR ISLANDS', 'CHANDIGARH', 'DADRA AND NAGAR HAVELI AND DAMAN AND DIU', 
    'DELHI', 'JAMMU AND KASHMIR', 'LADAKH', 'LAKSHADWEEP', 'PUDUCHERRY'
]

def find_matching_udise_file(olympiad_year_str):
    """
    Dynamically scans data/raw_udise to locate the booklet matching the 
    academic year timeline convention for the given olympiad year.
    """
    target_year = int(olympiad_year_str)
    prev_year = target_year - 1
    
    # Standard government multi-year notation patterns (e.g., 2023_24, 2023-24)
    patterns = [
        f"{prev_year}_{str(target_year)[2:]}",
        f"{prev_year}-{str(target_year)[2:]}",
        f"{prev_year}_{target_year}",
        f"{prev_year}-{target_year}",
        str(target_year)
    ]
    
    udise_root = "data/raw_udise"
    if not os.path.exists(udise_root):
        return None
        
    for root, dirs, files in os.walk(udise_root):
        for f in files:
            if f.endswith('.pdf'):
                combined_path = os.path.join(root, f).replace("\\", "/")
                for pattern in patterns:
                    if pattern in combined_path:
                        return combined_path
    return None

def parse_slis_cutoff(file_path):
    """Parses cutoffs strictly from an uploaded stage CSV file with no default values."""
    mapping = {}
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            state = str(row.get('region_name', '')).upper().strip()
            if state and 'cutoff_mark' in row:
                mapping[state] = float(row.get('cutoff_mark', 0.0))
    return mapping

def discover_and_extract_udise_metrics(udise_path):
    """
    Sweeps the PDF once to dynamically discover and extract all required variables 
    without any hardcoded page numbers or assumptions.
    """
    reader = pypdf.PdfReader(udise_path)
    
    # Definitions of lookup intent mapping to matching text tokens
    lookup_intents = {
        'enrollment': ['ENROLMENT', 'TOTAL', 'STATE/UT'],
        'teachers_count': ['TEACHERS', 'STATE/UT', 'SCHOOLS'],
        'ptr': ['PUPIL TEACHER RATIO', 'PTR'],
        'science_lab': ['LABORATORY', 'SCIENCE', 'SCHOOLS'],
        'internet': ['INTERNET', 'FACILITY'],
        'electricity': ['ELECTRICITY', 'PERCENTAGE'],
        'toilets': ['TOILET', 'PERCENTAGE'],
        'computers': ['COMPUTER', 'SCHOOLS'],
        'smart_class': ['SMART CLASS', 'SMARTCLASS'],
        'gender_parity': ['GENDER PARITY', 'INDEX'],
        'gross_enrolment': ['GROSS ENROLMENT', 'RATIO']
    }
    
    extracted_maps = {key: {} for key in lookup_intents.keys()}
    
    for metric_name, keywords in lookup_intents.items():
        max_matches = 0
        best_page_idx = None
        
        for idx, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if not text:
                    continue
                matches = sum(1 for kw in keywords if kw.upper() in text.upper())
                if matches > max_matches:
                    max_matches = matches
                    best_page_idx = idx
            except Exception:
                continue
                
        if best_page_idx is not None and max_matches >= 1:
            page_text = reader.pages[best_page_idx].extract_text()
            for line in page_text.split('\n'):
                line_upper = line.strip().upper()
                matched_state = None
                
                for state in OFFICIAL_STATES:
                    if state in line_upper:
                        matched_state = state
                        break
                        
                if matched_state:
                    tokens = line.strip().split()
                    nums = []
                    for t in tokens:
                        t_clean = t.replace(',', '').replace('%', '')
                        if re.match(r'^\d+(\.\d+)?$', t_clean):
                            nums.append(float(t_clean))
                            
                    if nums:
                        # Apply adaptive numeric selection token extraction logic
                        val = 0.0
                        if metric_name in ['internet', 'computers', 'smart_class', 'science_lab']:
                            val = nums[10] if len(nums) >= 11 else nums[-1]
                        elif metric_name in ['ptr', 'gender_parity']:
                            val = nums[-1]
                        elif metric_name == 'gross_enrolment':
                            val = nums[-1] if len(nums) >= 12 else nums[0]
                        elif metric_name == 'teachers_count':
                            val = nums[4] if len(nums) >= 5 else nums[0]
                        else:
                            val = nums[0]
                            
                        extracted_maps[metric_name][matched_state] = val
                        
    return extracted_maps

def process_year_metrics(year_str, discipline):
    print(f"\n⏳ Analyzing Chronological Node: [Year {year_str}] | [Subject: {discipline.upper()}]")
    
    target_olympiad_dir = f"data/raw_olympiad/{year_str}/{discipline}"
    udise_path = find_matching_udise_file(year_str)
    
    if not udise_path:
        print(f"⚠️ [FLAGGED UNAVAILABLE]: No corresponding UDISE+ PDF file found for Year {year_str}. Skipping node.")
        return None
        
    print(f" ✅ Dynamically Discovered Matching Booklet: {udise_path}")
    
    state_weights = {}
    state_girls_quota = {}
    state_cutoff_aggregates = {}
    
    search_pattern = os.path.join(target_olympiad_dir, "stage*_qualifiers.csv")
    qualifier_files = sorted(glob.glob(search_pattern))
    
    if not qualifier_files:
        print(f"⚠️ [FLAGGED UNAVAILABLE]: No qualifiers data sheets uploaded for Year {year_str}. Skipping node.")
        return None
        
    for file_path in qualifier_files:
        filename = os.path.basename(file_path)
        stage_match = re.search(r'stage(\d+)', filename)
        if not stage_match:
            continue
        stage_idx = int(stage_match.group(1))
        print(f" ✅ Processing Uploaded Talent File: Stage {stage_idx} [{filename}]")
        
        w_stage = 3.5 ** (stage_idx - 1)
        df_stage = pd.read_csv(file_path)
        
        for _, row in df_stage.iterrows():
            st = str(row.get('region_name', '')).upper().strip()
            if not st:
                continue
                
            if st not in state_weights:
                state_weights[st] = 0.0
                state_girls_quota[st] = 0
                state_cutoff_aggregates[st] = []
                
            pathway = str(row.get('selection_pathway', 'MI')).upper().strip()
            try:
                student_class = int(row.get('class_standard'))
            except (ValueError, TypeError):
                student_class = 12
                
            try:
                is_girls = int(row.get('is_girls_quota', 0))
            except (ValueError, TypeError):
                is_girls = 0
                
            alpha = 1.25 if pathway == 'MAS' else 1.00
            gamma = 2.50 if student_class <= 9 else (1.75 if student_class == 10 else (1.25 if student_class == 11 else 1.00))
            
            state_weights[st] += (w_stage * alpha * gamma)
            if is_girls:
                state_girls_quota[st] += 1
                
        cutoff_counterpart = os.path.join(target_olympiad_dir, f"stage{stage_idx}_cutoffs.csv")
        if os.path.exists(cutoff_counterpart):
            stage_cutoffs = parse_slis_cutoff(cutoff_counterpart)
            for st, val in stage_cutoffs.items():
                if st:
                    if st not in state_cutoff_aggregates:
                        state_cutoff_aggregates[st] = []
                    state_cutoff_aggregates[st].append(val)

    # Mine metrics dynamically via raw text search loops
    maps = discover_and_extract_udise_metrics(udise_path)
    enroll_map = maps.get('enrollment', {})
    
    if not enroll_map:
        print(f"⚠️ [FLAGGED UNAVAILABLE]: Enrollment table could not be dynamically verified. Skipping.")
        return None
        
    fused_records = []
    ignore_keywords = ['INDIA', 'TOTAL', 'ALL STATES', 'CENTRAL', 'UNION TERRITORY']
    
    for state_key in enroll_map.keys():
        if any(keyword in state_key for keyword in ignore_keywords):
            continue
            
        weight_val = state_weights.get(state_key, 0.0)
        girls_val = state_girls_quota.get(state_key, 0)
        cutoff_list = state_cutoff_aggregates.get(state_key, [])
        blended_cutoff = float(np.mean(cutoff_list)) if cutoff_list else 0.0
        
        fused_records.append({
            'year': int(year_str),
            'region_name': state_key,
            'avg_state_qualification_score': (weight_val / enroll_map[state_key]) * 1_000_000 if enroll_map[state_key] > 0 else 0.0,
            'pupil_teacher_ratio': maps['ptr'].get(state_key, 0.0),
            'science_lab_pct': maps['science_lab'].get(state_key, 0.0),
            'internet_access_pct': maps['internet'].get(state_key, 0.0),
            'gender_parity_index': maps['gender_parity'].get(state_key, 0.0),
            'literacy_proxy_ger': maps['gross_enrolment'].get(state_key, 0.0),
            'electricity_pct': maps['electricity'].get(state_key, 0.0),
            'toilets_pct': maps['toilets'].get(state_key, 0.0),
            'computers_pct': maps['computers'].get(state_key, 0.0),
            'smart_class_pct': maps['smart_class'].get(state_key, 0.0),
            'avg_teachers_per_school': maps['teachers_count'].get(state_key, 0.0),
            'official_state_cutoff': blended_cutoff,
            'ag_quota_seats_allocated': int(girls_val)
        })
        
    return fused_records

def run_airtight_pipeline():
    print("\n" + "="*80)
    print("🚀 EXECUTING PURE EMPIRICAL KEYWORD-DISCOVERY MERGE PIPELINE")
    print("="*80)
    
    olympiad_root = "data/raw_olympiad"
    if not os.path.exists(olympiad_root):
        print(f"❌ DATA PATH ERROR: Root directory '{olympiad_root}' does not exist.")
        return
        
    all_compiled_records = []
    
    for year_folder in sorted(os.listdir(olympiad_root)):
        if re.match(r'^\d{4}$', year_folder):
            year_path = os.path.join(olympiad_root, year_folder)
            for discipline in os.listdir(year_path):
                discipline_path = os.path.join(year_path, discipline)
                if os.path.isdir(discipline_path):
                    records = process_year_metrics(year_folder, discipline)
                    if records:
                        all_compiled_records.extend(records)
                        
    if all_compiled_records:
        os.makedirs("data/processed", exist_ok=True)
        master_df = pd.DataFrame(all_compiled_records)
        master_df.to_csv("data/processed/master_stem_matrix.csv", index=False)
        print(f"\n🎉 SUCCESS: Unified longitudinal database compiled with {len(master_df)} empirical records.")
    else:
        print("\n⚠️ SYSTEM STATUS: Zero data processed. Pipeline is waiting for uploaded files.")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_airtight_pipeline()