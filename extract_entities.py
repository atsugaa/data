#!/usr/bin/env python3
"""
Entity extraction script for court decision documents.
Extracts structured information from txt files and updates extract.json
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional

# Load already processed files from list.txt
def load_processed_files(list_file: str = "list.txt") -> set:
    """Load the list of already processed files"""
    processed = set()
    if os.path.exists(list_file):
        with open(list_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    processed.add(line)
    return processed

def save_processed_file(list_file: str, filepath: str):
    """Append a processed file to the list"""
    with open(list_file, 'a', encoding='utf-8') as f:
        f.write(f"{filepath}\n")

def extract_case_number(text: str) -> str:
    """Extract case number (nomor perkara)"""
    patterns = [
        r'Nomor\s+(\d+/[^\n]+)',
        r'NOMOR\s+(\d+/[^\n]+)',
        r'Perkara\s+Nomor\s+(\d+/[^\n]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""

def extract_decision_date(text: str) -> str:
    """Extract decision date (tanggal putusan)"""
    # Look for date patterns near the beginning
    patterns = [
        r'(?:tanggal|Tanggal)\s+(\d{1,2}\s+\w+\s+\d{4})',
        r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember|Nopember)\s+\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text[:2000])
        if match:
            return match.group(1).strip()
    return ""

def extract_court_location(text: str) -> str:
    """Extract court location"""
    patterns = [
        r'Pengadilan\s+Negeri\s+([^\n]+?)(?:\s+yang|$)',
        r'PN\s+([A-Z][a-z]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text[:500])
        if match:
            location = match.group(1).strip()
            # Clean up common patterns
            location = re.sub(r'\s+yang.*', '', location)
            return f"PN {location}"
    return ""

def extract_defendant_info(text: str) -> List[Dict]:
    """Extract defendant information"""
    defendants = []
    
    # Look for defendant section
    defendant_pattern = r'(?:Terdakwa|TERDAKWA)\s*:\s*([^\n]+)'
    matches = re.finditer(defendant_pattern, text[:3000])
    
    for match in matches:
        defendant = {
            "nama": "",
            "umur": "",
            "tempat_lahir": "",
            "tanggal_lahir": "",
            "jenis_kelamin": "",
            "kebangsaan": "Indonesia",
            "agama": "",
            "pekerjaan": "",
            "alamat": {
                "kelurahan": "",
                "kecamatan": "",
                "kabupaten": "",
                "kota": "",
                "alamat_lengkap": ""
            },
            "tuntutan_pidana": [],
            "tuntutan_hukuman": {"jenis": "", "lama": ""},
            "putusan_pidana": "",
            "putusan_hukuman": {"jenis": "", "lama": ""}
        }
        
        # Extract basic info from structured format
        start_pos = match.start()
        section = text[start_pos:start_pos+2000]
        
        # Name
        name_match = re.search(r'Nama\s+lengkap\s*:\s*([^\n]+)', section, re.IGNORECASE)
        if name_match:
            defendant["nama"] = name_match.group(1).strip()
        
        # Age/Birth date
        age_match = re.search(r'Umur/Tanggal\s+lahir\s*:\s*([^\n]+)', section, re.IGNORECASE)
        if age_match:
            age_info = age_match.group(1).strip()
            defendant["umur"] = age_info
            # Try to extract tanggal_lahir if present
            date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', age_info)
            if date_match:
                defendant["tanggal_lahir"] = date_match.group(1)
        
        # Birth place
        birth_match = re.search(r'Tempat\s+lahir\s*:\s*([^\n]+)', section, re.IGNORECASE)
        if birth_match:
            defendant["tempat_lahir"] = birth_match.group(1).strip()
        
        # Gender
        gender_match = re.search(r'Jenis\s+kelamin\s*:\s*([^\n]+)', section, re.IGNORECASE)
        if gender_match:
            defendant["jenis_kelamin"] = gender_match.group(1).strip()
        
        # Religion
        religion_match = re.search(r'Agama\s*:\s*([^\n]+)', section, re.IGNORECASE)
        if religion_match:
            defendant["agama"] = religion_match.group(1).strip()
        
        # Occupation
        job_match = re.search(r'Pekerjaan\s*:\s*([^\n]+)', section, re.IGNORECASE)
        if job_match:
            defendant["pekerjaan"] = job_match.group(1).strip()
        
        # Address
        addr_match = re.search(r'Tempat\s+tinggal\s*:\s*([^\n]+)', section, re.IGNORECASE)
        if addr_match:
            defendant["alamat"]["alamat_lengkap"] = addr_match.group(1).strip()
        
        defendants.append(defendant)
    
    return defendants if defendants else [{}]

def extract_judges(text: str) -> List[Dict]:
    """Extract judge information"""
    judges = []
    
    # Look for judge mentions
    judge_section = re.search(r'Majelis\s+Hakim.*?(?=Panitera|Penuntut|$)', text, re.IGNORECASE | re.DOTALL)
    if judge_section:
        section_text = judge_section.group(0)
        
        # Extract names
        names = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*S\.H\.(?:,\s*M\.H\.)?)?)', section_text)
        
        if names:
            judges.append({
                "ketua": names[0] if len(names) > 0 else "",
                "anggota": [{"nama": name} for name in names[1:3]]
            })
    
    return judges if judges else [{"ketua": "", "anggota": []}]

def extract_officials(text: str) -> Dict[str, str]:
    """Extract court officials (panitera, penuntut_umum, penasehat_hukum)"""
    officials = {
        "panitera": "",
        "penuntut_umum": "",
        "penasehat_hukum": ""
    }
    
    # Panitera
    panitera_match = re.search(r'Panitera\s*:\s*([^\n]+)', text, re.IGNORECASE)
    if panitera_match:
        officials["panitera"] = panitera_match.group(1).strip()
    
    # Penuntut Umum
    prosecutor_match = re.search(r'Penuntut\s+Umum\s*:\s*([^\n]+)', text, re.IGNORECASE)
    if prosecutor_match:
        officials["penuntut_umum"] = prosecutor_match.group(1).strip()
    
    # Penasehat Hukum
    lawyer_match = re.search(r'Penasehat\s+Hukum\s*:\s*([^\n]+)', text, re.IGNORECASE)
    if lawyer_match:
        officials["penasehat_hukum"] = lawyer_match.group(1).strip()
    
    return officials

def extract_entities(file_path: str) -> Optional[Dict]:
    """Main extraction function for a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # Create normalized path for consistency
        normalized_path = file_path.replace('/home/runner/work/data/', '')
        
        # Extract all entities
        entry = {
            "nomor_perkara": extract_case_number(text),
            "tanggal_putusan": extract_decision_date(text),
            "lokasi": extract_court_location(text),
            "terdakwa": extract_defendant_info(text),
            "hakim": extract_judges(text),
            "panitera": extract_officials(text)["panitera"],
            "penuntut_umum": extract_officials(text)["penuntut_umum"],
            "penasehat_hukum": extract_officials(text)["penasehat_hukum"],
            "nama_file": normalized_path,
            "url": ""
        }
        
        return entry
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    """Main execution function"""
    # Load existing data
    extract_file = "extract.json"
    list_file = "list.txt"
    
    print("Loading existing data...")
    with open(extract_file, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    print(f"Existing entries: {len(existing_data)}")
    
    # Load processed files
    processed_files = load_processed_files(list_file)
    print(f"Already processed: {len(processed_files)} files")
    
    # Find all txt files
    txt_files = []
    for pn_dir in Path('.').glob('pn-*'):
        if pn_dir.is_dir():
            txt_dir = pn_dir / 'txt'
            if txt_dir.exists():
                for txt_file in txt_dir.glob('*.txt'):
                    if '.ipynb_checkpoints' not in str(txt_file):
                        txt_files.append(txt_file)
    
    print(f"Total txt files found: {len(txt_files)}")
    
    # Filter out already processed files
    files_to_process = []
    for txt_file in txt_files:
        # Create normalized path
        normalized = str(txt_file).replace('/home/runner/work/data/', '')
        if normalized not in processed_files:
            files_to_process.append((txt_file, normalized))
    
    print(f"Files to process: {len(files_to_process)}")
    
    # Process files in batches
    batch_size = 100
    new_entries = []
    processed_count = 0
    
    for i, (file_path, normalized_path) in enumerate(files_to_process):
        if i >= 1000:  # Limit for this run to avoid timeout
            print(f"Processed {i} files. Stopping to save progress...")
            break
        
        entry = extract_entities(str(file_path))
        if entry:
            new_entries.append(entry)
            save_processed_file(list_file, normalized_path)
            processed_count += 1
        
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} files...")
    
    # Append new entries to existing data
    existing_data.extend(new_entries)
    
    # Save updated extract.json
    print(f"\nSaving {len(new_entries)} new entries...")
    with open(extract_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nExtraction complete!")
    print(f"Total entries in extract.json: {len(existing_data)}")
    print(f"Newly processed: {processed_count}")

if __name__ == "__main__":
    main()
