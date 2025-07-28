# main.py
# Round 1A: PDF Outline Extraction with robust heading logic (V4)

import fitz  # PyMuPDF
import json
import os
import re
from collections import Counter

# --- Fixed container paths ---
INPUT_DIR = '/app/input'
OUTPUT_DIR = '/app/output'
PDF_SOURCE_DIR = os.path.join(INPUT_DIR, 'pdfs') if os.path.isdir(os.path.join(INPUT_DIR, 'pdfs')) else INPUT_DIR

# --- Helper: Analyze document font styles ---
def get_document_stats(doc):
    stats = {'sizes': Counter(), 'fonts': Counter(), 'body_size': 10, 'body_font': 'Times'}
    for page_num, page in enumerate(doc):
        if page_num > 5 and doc.page_count > 10:
            continue
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        stats['sizes'][round(s['size'])] += 1
                        stats['fonts'][s['font']] += 1
    if stats['sizes']:
        stats['body_size'] = stats['sizes'].most_common(1)[0][0]
    if stats['fonts']:
        stats['body_font'] = stats['fonts'].most_common(1)[0][0]
    return stats

# --- Core extraction logic ---
def extract_outline_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return None

    title = doc.metadata.get('title', '').strip()
    if not title:
        try:
            page = doc.load_page(0)
            title_text = page.get_text(clip=(0, 0, page.rect.width, page.rect.height * 0.25))
            title = ' '.join(title_text.split())
        except Exception:
            title = os.path.basename(pdf_path)
    if not title:
        title = os.path.basename(pdf_path)

    stats = get_document_stats(doc)
    body_size = stats['body_size']

    potential_headings = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXTFLAGS_SEARCH)["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    if l["spans"]:
                        line_text = " ".join([s["text"] for s in l["spans"]]).strip()
                        if not line_text or len(line_text) > 250:
                            continue

                        span = l["spans"][0]
                        font_size = round(span["size"])
                        is_bold = "bold" in span["font"].lower()

                        if l['bbox'][1] > page.rect.height * 0.9 or re.match(r'^\s*\d+\s*$', line_text):
                            continue

                        potential_headings.append({
                            "text": line_text, "page": page_num + 1, "bbox": l["bbox"],
                            "size": font_size, "bold": is_bold
                        })

    outline = []
    for head in potential_headings:
        level = None
        text = head['text']

        appendix_match = re.match(r'^\s*Appendix\s+[A-Z]', text, re.IGNORECASE)
        num_match = re.match(r'^\s*(\d+(\.\d+)*)\s+', text)

        if appendix_match:
            level = 'H1'
        elif num_match:
            depth = len(num_match.group(1).split('.'))
            level = f"H{depth}" if depth <= 4 else "H4"
        else:
            is_stylistic = (head['size'] > body_size + 2) or (head['bold'] and head['size'] > body_size)
            if is_stylistic and len(text.split()) < 15:
                if head['size'] > body_size * 1.4:
                    level = "H1"
                elif head['size'] > body_size * 1.15:
                    level = "H2"
                else:
                    level = "H3"

        if level:
            outline.append({
                "level": level, "text": text, "page": head['page'],
                "bbox": head['bbox'], "style": (head['size'], head['bold'])
            })

    if not outline:
        return {"title": title, "outline": []}

    outline.sort(key=lambda x: (x["page"], x["bbox"][1]))
    merged_headings = []
    current_heading = outline[0]

    for i in range(1, len(outline)):
        next_heading = outline[i]
        y_dist = next_heading["bbox"][1] - current_heading["bbox"][3]

        if (next_heading["page"] == current_heading["page"] and
            next_heading["style"] == current_heading["style"] and
            next_heading["level"] == current_heading["level"] and
            0 <= y_dist < 15):
            current_heading["text"] += " " + next_heading["text"]
            current_heading["bbox"] = (
                min(current_heading["bbox"][0], next_heading["bbox"][0]),
                min(current_heading["bbox"][1], next_heading["bbox"][1]),
                max(current_heading["bbox"][2], next_heading["bbox"][2]),
                max(current_heading["bbox"][3], next_heading["bbox"][3])
            )
        else:
            merged_headings.append(current_heading)
            current_heading = next_heading
    merged_headings.append(current_heading)

    final_outline = [{"level": h["level"], "text": h["text"], "page": h["page"]} for h in merged_headings]

    return {"title": title, "outline": final_outline}

# --- Entry Point ---
if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(PDF_SOURCE_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(PDF_SOURCE_DIR, filename)
            print(f"Processing {pdf_path}...")

            structured_data = extract_outline_from_pdf(pdf_path)

            if structured_data:
                output_filename = os.path.splitext(filename)[0] + ".json"
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=4, ensure_ascii=False)
                print(f"✅ Successfully created outline at {output_path}")
