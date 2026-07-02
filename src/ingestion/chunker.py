import os
import glob
import json
import logging
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DATA_PATH, RAW_DATA_PATH, SCHEMES

def extract_section(text: str, start_marker: str, end_markers: list) -> str:
    """Helper to extract text between a start marker and the first found end marker."""
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return ""
    
    sub_text = text[start_idx:]
    end_idx = len(sub_text)
    for marker in end_markers:
        idx = sub_text.find(marker, len(start_marker))
        if idx != -1 and idx < end_idx:
            end_idx = idx
            
    return sub_text[:end_idx].strip()

def build_semantic_chunks(slug: str, text: str, scheme_data: dict, scrape_date: str) -> list:
    """Parses text into semantic chunks and injects rich metadata."""
    chunks = []
    
    header_prefix = f"[Fund: {scheme_data['name']} | Category: {scheme_data['category']}]\n"
    
    # 1. Overview Section
    nav_match = re.search(r"NAV:.*?\n(₹[0-9.,]+)", text)
    aum_match = re.search(r"Fund size \(AUM\)\n(₹[0-9.,]+ Cr)", text)
    expense_match = re.search(r"Expense ratio\n([0-9.]+%?)", text)
    rating_match = re.search(r"Rating\n([0-9]+)", text)
    
    overview_lines = ["[Section: Fund Overview]"]
    if nav_match: overview_lines.append(f"NAV: {nav_match.group(1)}")
    if aum_match: overview_lines.append(f"Fund Size (AUM): {aum_match.group(1)}")
    if expense_match: overview_lines.append(f"Expense Ratio: {expense_match.group(1)}")
    if rating_match: overview_lines.append(f"Rating: {rating_match.group(1)}")
    
    if len(overview_lines) > 1:
        chunks.append({
            "chunk_id": f"{slug}_overview",
            "content": header_prefix + "\n".join(overview_lines),
            "scheme_name": scheme_data["name"],
            "category": scheme_data["category"],
            "source_url": scheme_data["url"],
            "scrape_date": scrape_date
        })

    # 2. Holdings
    holdings_text = extract_section(text, "Name | Sector | Instruments", ["Minimum investments", "Understand terms"])
    if holdings_text:
        chunks.append({
            "chunk_id": f"{slug}_holdings",
            "content": header_prefix + "[Section: Top Holdings & Asset Allocation]\n" + holdings_text,
            "scheme_name": scheme_data["name"],
            "category": scheme_data["category"],
            "source_url": scheme_data["url"],
            "scrape_date": scrape_date
        })

    # 3. Minimum Investments
    min_inv_text = extract_section(text, "Minimum investments", ["Understand terms", "Returns and rankings"])
    if min_inv_text:
        chunks.append({
            "chunk_id": f"{slug}_minimum_investments",
            "content": header_prefix + "[Section: Minimum Investments]\n" + min_inv_text,
            "scheme_name": scheme_data["name"],
            "category": scheme_data["category"],
            "source_url": scheme_data["url"],
            "scrape_date": scrape_date
        })

    # 4. Returns & Rankings
    returns_text = extract_section(text, "Name | 3Y | 5Y", ["Understand terms", "Exit load"])
    if returns_text:
        chunks.append({
            "chunk_id": f"{slug}_returns",
            "content": header_prefix + "[Section: Historic Returns & Rankings]\n" + returns_text,
            "scheme_name": scheme_data["name"],
            "category": scheme_data["category"],
            "source_url": scheme_data["url"],
            "scrape_date": scrape_date
        })

    # 5. Exit Load & Tax
    tax_text = extract_section(text, "Exit load, stamp duty and tax", ["Check past data", "Fund management", "Similar funds"])
    if tax_text:
        chunks.append({
            "chunk_id": f"{slug}_tax_exit_load",
            "content": header_prefix + "[Section: Exit Load, Stamp Duty & Tax Implications]\n" + tax_text,
            "scheme_name": scheme_data["name"],
            "category": scheme_data["category"],
            "source_url": scheme_data["url"],
            "scrape_date": scrape_date
        })
        
    # 6. Fund Management
    mgmt_text = extract_section(text, "Fund management", ["Similar funds", "Other funds"])
    if mgmt_text:
        chunks.append({
            "chunk_id": f"{slug}_management",
            "content": header_prefix + "[Section: Fund Management]\n" + mgmt_text,
            "scheme_name": scheme_data["name"],
            "category": scheme_data["category"],
            "source_url": scheme_data["url"],
            "scrape_date": scrape_date
        })

    return chunks


def main():
    txt_files = glob.glob(os.path.join(PROCESSED_DATA_PATH, "*.txt"))
    logging.info(f"Found {len(txt_files)} cleaned text files for chunking.")
    
    total_chunks = 0
    
    for file_path in txt_files:
        basename = os.path.basename(file_path)
        slug = basename.replace(".txt", "")
        
        if slug not in SCHEMES:
            logging.warning(f"Skipping {slug} - not found in config.SCHEMES")
            continue
            
        scheme_data = SCHEMES[slug]
        
        # Load meta to get scrape_date
        meta_path = os.path.join(RAW_DATA_PATH, f"{slug}_meta.json")
        scrape_date = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                scrape_date = json.load(f).get("scrape_date", scrape_date)
                
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        chunks = build_semantic_chunks(slug, text, scheme_data, scrape_date)
        
        # Save chunks to JSON
        out_path = os.path.join(PROCESSED_DATA_PATH, f"{slug}_chunks.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=4)
            
        logging.info(f"Generated {len(chunks)} semantic chunks for {slug}")
        total_chunks += len(chunks)
        
    logging.info(f"Chunking completed. Generated {total_chunks} total chunks.")

if __name__ == "__main__":
    main()
