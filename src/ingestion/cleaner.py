import os
import glob
import logging
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Import config
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RAW_DATA_PATH, PROCESSED_DATA_PATH

def clean_html(html_content: str) -> str:
    """Parses HTML, formats tables to key-value pairs, and extracts clean text."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Remove unnecessary HTML elements
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "svg", "button", "iframe"]):
        element.decompose()
        
    # 2. Extract structured data from Tables
    # Groww often puts important fund info (Expense Ratio, Exit Load, etc.) in tables
    for table in soup.find_all("table"):
        table_text = []
        for row in table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            cols_text = [col.get_text(separator=" ", strip=True) for col in cols]
            if len(cols_text) == 2:
                # Format as Key: Value
                table_text.append(f"{cols_text[0]}: {cols_text[1]}")
            else:
                table_text.append(" | ".join(cols_text))
        
        # Replace the HTML table with our clean text representation
        if table_text:
            new_text = soup.new_string("\n" + "\n".join(table_text) + "\n")
            table.replace_with(new_text)

    # 3. Extract the remaining text
    text = soup.get_text(separator="\n")
    
    # 4. Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    # Drop completely blank lines
    cleaned_text = "\n".join(line for line in lines if line)
    
    return cleaned_text

def main():
    html_files = glob.glob(os.path.join(RAW_DATA_PATH, "*.html"))
    logging.info(f"Found {len(html_files)} HTML files to process.")
    
    for file_path in html_files:
        basename = os.path.basename(file_path)
        slug = basename.replace(".html", "")
        
        logging.info(f"Processing {slug}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        cleaned_text = clean_html(html_content)
        
        output_path = os.path.join(PROCESSED_DATA_PATH, f"{slug}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
            
        logging.info(f"Saved cleaned text to {output_path} ({len(cleaned_text)} chars)")

    logging.info("Data cleaning completed.")

if __name__ == "__main__":
    main()
