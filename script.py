import os
import json
import time
import logging
import shutil
from typing import List, Dict
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np

# ---------- Logging Setup ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# ---------- FOLDER SETUP ----------
def ensure_folders_exist():
    """Create input and output folders if they don't exist."""
    folders = ['input', 'output']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            logging.info(f"Created folder: {folder}")
        else:
            logging.info(f"Folder already exists: {folder}")

def find_pdf_files():
    """Find all PDF files in the input folder."""
    pdf_files = []
    input_folder = 'input'
    if os.path.exists(input_folder):
        for file in os.listdir(input_folder):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(input_folder, file))
    return pdf_files

# -------- Model Loading (ensure pre-download if offline!) ---------
MODEL_PATH = 'all-MiniLM-L6-v2'  # Should fit <1GB. Download before if offline.
try:
    model = SentenceTransformer(MODEL_PATH)
    logging.info(f"SentenceTransformer model loaded from {MODEL_PATH}")
except Exception as e:
    logging.critical(f"Could not load SentenceTransformer model: {e}")
    raise

# ---------- PDF SECTION EXTRACTION ----------
def extract_sections(pdf_path: str) -> List[Dict]:
    """
    Extracts sections from a PDF using simple heuristics.
    Each section is defined by a block separated by double newlines.
    """
    sections = []
    try:
        reader = PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if not text:
                    logging.warning(f"No text extracted on page {page_num+1} of {os.path.basename(pdf_path)}")
                    continue
                # Naively split sections: double newline as separator
                parts = text.split('\n\n')
                for idx, part in enumerate(parts):
                    lines = [line.strip() for line in part.split('\n') if line.strip()]
                    if not lines:
                        continue
                    title = lines[0][:50]
                    section_text = '\n'.join(lines)
                    sections.append({
                        "document": os.path.basename(pdf_path),
                        "page_number": page_num + 1,
                        "section_title": title,
                        "section_text": section_text,
                    })
            except Exception as e:
                logging.error(f"Error extracting page {page_num+1} from {pdf_path}: {e}")
    except Exception as e:
        logging.error(f"Error opening/reading {pdf_path}: {e}")
    return sections

# ---------- EMBEDDING & RELEVANCE ----------
def embed_texts(texts: List[str]):
    try:
        return model.encode(texts)
    except Exception as e:
        logging.error(f"Error embedding texts: {e}")
        return np.zeros((len(texts), model.get_sentence_embedding_dimension()))

def compute_relevance(section_texts: List[str], query: str) -> List[float]:
    """
    Computes semantic similarity (cosine) between section texts and a persona/job query.
    """
    section_embeds = embed_texts(section_texts)
    try:
        query_embed = model.encode([query])[0]
    except Exception as e:
        logging.error(f"Error embedding query: {e}")
        query_embed = np.zeros(model.get_sentence_embedding_dimension())
    denom = np.linalg.norm(section_embeds, axis=1) * (np.linalg.norm(query_embed) + 1e-8)
    dot = np.dot(section_embeds, query_embed)
    similarities = dot / (denom + 1e-8)
    return similarities.tolist()

# ---------- SUB-SECTION ANALYSIS ----------
def analyze_subsections(section: Dict, query: str) -> List[Dict]:
    """
    Further breaks down a section into lines (or small sub-sections) and
    ranks them for relevance to the query.
    """
    lines = [l.strip() for l in section['section_text'].split('\n') if l.strip()]
    if not lines:
        return []
    relevances = compute_relevance(lines, query)
    # Only return sub-sections above a threshold (tuned as needed)
    threshold = 0.5
    results = []
    for text, score in zip(lines, relevances):
        if score > threshold:
            results.append({
                "document": section["document"],
                "refined_text": text,
                "page_number": section["page_number"]
            })
    return results

# ---------- MAIN PROCESSING FUNCTION ----------
def process_documents(pdf_paths: List[str], persona: str, job: str) -> Dict:
    all_sections = []
    section_texts = []
    # Extract all sections across PDFs
    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            logging.error(f"File not found: {pdf_path}")
            continue
        secs = extract_sections(pdf_path)
        all_sections.extend(secs)
        section_texts.extend([s['section_text'] for s in secs])
    if not all_sections:
        logging.error("No sections extracted from any PDF! Exiting.")
        raise RuntimeError("No valid PDF content.")

    # Build combined query
    query = f"{persona}. TASK: {job}"
    section_scores = compute_relevance(section_texts, query)
    # Rank by relevance; take top K (configurable)
    K = min(10, len(all_sections))
    ranked = sorted(zip(all_sections, section_scores), key=lambda x: -x[1])[:K]

    output_sections = []
    subsection_analyses = []
    for rank, (section, score) in enumerate(ranked, 1):
        output_sections.append({
            "document": section["document"],
            "page_number": section["page_number"],
            "section_title": section["section_title"],
            "importance_rank": rank
        })
        # Run refined sub-section analysis
        subs = analyze_subsections(section, query)
        subsection_analyses.extend(subs)

    result = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in pdf_paths],
            "persona": persona,
            "job-to-be-done": job,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "extracted_sections": output_sections,
        "subsection_analyses": subsection_analyses
    }
    return result

# ---------- MAIN EXECUTION ----------
if __name__ == "__main__":
    try:
        # ---- Replace with real input filenames and persona/job ---
        pdfs = ['sample1.pdf', 'sample2.pdf']
        persona = "Academic Researcher in Machine Learning"
        job = "Survey literature on recent advances in large language models"
        output_json = "challenge1b_output.json"

        # Ensure input and output folders exist
        ensure_folders_exist()

        # Update PDF paths to use input folder
        input_pdfs = [os.path.join('input', os.path.basename(pdf)) for pdf in pdfs]
        
        # Copy input PDFs to the 'input' folder if they exist in current directory
        copied_files = []
        for pdf_path in pdfs:
            if os.path.exists(pdf_path):
                new_path = os.path.join('input', os.path.basename(pdf_path))
                try:
                    shutil.copy2(pdf_path, new_path)
                    logging.info(f"Copied {pdf_path} to {new_path}")
                    copied_files.append(new_path)
                except Exception as e:
                    logging.error(f"Error copying {pdf_path} to {new_path}: {e}")
            else:
                logging.warning(f"Input file not found: {pdf_path}")

        # Find all available PDF files in the input folder
        available_pdfs = find_pdf_files()
        
        if not available_pdfs:
            logging.error("No PDF files found to process!")
            logging.info("Please place your PDF files in the 'input' folder or in the current directory.")
            logging.info("Expected files: sample1.pdf, sample2.pdf")
            logging.info("You can modify the 'pdfs' list in the script to match your actual file names.")
            logging.info("Alternatively, place any PDF files in the 'input' folder and they will be automatically detected.")
            exit(1)

        logging.info(f"Found {len(available_pdfs)} PDF files to process: {[os.path.basename(pdf) for pdf in available_pdfs]}")

        # Process documents from the available PDFs
        result = process_documents(available_pdfs, persona, job)

        # Save output to the 'output' folder
        output_path = os.path.join('output', output_json)
        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logging.info(f"Processing complete. Output written to {output_path}.")
    except Exception as exc:
        logging.critical(f"Fatal error in main workflow: {exc}", exc_info=True)
