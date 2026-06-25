import pypdf
import pandas as pd
import os

def isolate_udise_tables(pdf_path):
    """
    Scans the UDISE+ booklet, targets the specific structural pages 
    for PTR and Science Labs, and extracts raw state rows.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Could not locate the PDF at {pdf_path}. Please check your folders.")
        
    reader = pypdf.PdfReader(pdf_path)
    ptr_records = []
    science_lab_records = []
    
    print("Scanning UDISE+ Booklet pages for target matrices...")
    
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        
        # Target Table 4.12: Pupil Teacher Ratio (PTR)
        if "Table 4.12" in text or (idx >= 55 and idx <= 65 and "Pupil Teacher Ratio" in text):
            lines = text.split("\n")
            for line in lines:
                # Look for lines starting with a state pattern or numerical indexes
                # e.g., "1 ANDHRA PRADESH 24 19" or similar tabular formats
                parts = line.strip().split()
                if len(parts) >= 3 and parts[0].isdigit():
                    # High-level clean: filter out years or page numbers
                    if not any(x in line.upper() for x in ["TOTAL", "INDIA", "REPORT", "MULTIPLY"]):
                        ptr_records.append(line)
                        
        # Target Table 7.23: Integrated Science Lab Facility
        if "Table 7.23" in text or (idx >= 135 and idx <= 145 and "Science Lab" in text):
            lines = text.split("\n")
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 3 and parts[0].isdigit():
                    if not any(x in line.upper() for x in ["TOTAL", "INDIA", "BOOKLET"]):
                        science_lab_records.append(line)

    # Save raw isolated lines to text blocks inside data folder for verification
    with open("data/raw_udise/isolated_ptr.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(ptr_records))
        
    with open("data/raw_udise/isolated_labs.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(science_lab_records))
        
    print(f"Extraction complete! Isolated entries saved to data/raw_udise/ folder.")
    return len(ptr_records), len(science_lab_records)

if __name__ == "__main__":
    # Test path pointing directly to your local file
    pdf_location = "data/raw_udise/UDISE+2023_24_Booklet_nep.pdf"
    try:
        isolate_udise_tables(pdf_location)
    except Exception as e:
        print(f"Run status: {e}")