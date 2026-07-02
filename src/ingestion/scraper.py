import os
import time
import json
import logging
from datetime import datetime
import requests
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Import config (adjust path dynamically for running as script)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCHEMES, RAW_DATA_PATH

def scrape_url(url: str, retries=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    for attempt in range(retries):
        try:
            logging.info(f"Scraping {url} (Attempt {attempt+1}/{retries})...")
            response = requests.get(url, headers=headers, timeout=30)
            
            # Detect rate limiting
            if response.status_code in [403, 429]:
                logging.warning(f"Rate limited (Status {response.status_code}). Waiting before retry...")
                time.sleep(5)
                continue
                
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            time.sleep(3)
            
    logging.error(f"Failed to fetch {url} after {retries} attempts.")
    return None

def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
        
    # Get text
    text = soup.get_text(separator="\n")
    
    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)
    return text

def main():
    logging.info(f"Starting web scraper for {len(SCHEMES)} schemes.")
    scrape_date = datetime.now().isoformat()
    
    for slug, scheme_data in SCHEMES.items():
        url = scheme_data["url"]
        html_content = scrape_url(url)
        
        if html_content:
            # Save raw HTML
            html_path = os.path.join(RAW_DATA_PATH, f"{slug}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            # Extract and save text
            text_content = extract_text_from_html(html_content)
            text_path = os.path.join(RAW_DATA_PATH, f"{slug}.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text_content)
                
            # Save metadata
            meta_path = os.path.join(RAW_DATA_PATH, f"{slug}_meta.json")
            metadata = {
                "slug": slug,
                "name": scheme_data["name"],
                "category": scheme_data["category"],
                "url": url,
                "scrape_date": scrape_date,
                "html_size_bytes": len(html_content),
                "text_size_bytes": len(text_content)
            }
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
                
            logging.info(f"Successfully processed {slug}. HTML: {len(html_content)} bytes, Text: {len(text_content)} bytes.")
            
        # Polite delay between requests
        time.sleep(2)
        
    logging.info("Scraping completed.")

if __name__ == "__main__":
    main()
