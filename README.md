# Adobe-India-Connecting-the-Dots-Challenge-2025_1A

## Adobe India Hackathon 2025: Round 1A - Document Outline Extractor  
**Submission for the "Connecting the Dots" Challenge**

This repository contains the complete solution for Round 1A. The objective is to develop a robust and efficient service that extracts a structured outline (Title, H1, H2, H3) from PDF documents, with a focus on accurately handling complex, real-world files.

---

## Our Methodology

The primary challenge in this task is the unreliable nature of PDF structures. Simply relying on a single attribute like font size is insufficient for accurate heading detection. Our solution overcomes this by implementing a multi-signal heuristic engine, which analyzes documents with a layered approach that prioritizes structural cues over purely stylistic ones.

### 1. Statistical Baseline Analysis

Before processing, the script performs a quick analysis of the document's typography to establish a statistical baseline. It identifies the most common font and size, which are assumed to represent the main body text. This "style fingerprint" is crucial for making context-aware decisions about what constitutes a heading.

### 2. Multi-Signal Heading Identification

Our engine evaluates each line of text against a hierarchy of signals to determine if it qualifies as a heading:

- **Structural Patterns (Highest Priority):** The most reliable indicators of a heading are structural markers. We use regular expressions to detect common academic and technical formatting, such as `Appendix A:`, `1. Introduction`, or `2.1. Methodology`. The numbering depth (e.g., 2.1.1) directly maps to the heading level (H1, H2, H3).

- **Stylistic Patterns (Secondary Priority):** If no structural pattern is found, the engine analyzes the line's visual style. A line is flagged as a stylistic heading if it is bold and has a font size larger than the body text, or if its font size is significantly larger. This effectively captures unnumbered headings like "Summary" or "Conclusion."

### 3. Intelligent Merging of Multi-Line Headings

PDFs often contain headings that span multiple lines. Our solution includes a post-processing step that intelligently merges these. It examines consecutive heading candidates, and if they share the same style (font, size, boldness) and are vertically close on the page, they are combined into a single, coherent heading.

### 4. Filtering and Cleaning

To maximize accuracy, the script methodically filters out common false positives. It ignores text in the footer region of the page and discards lines that consist solely of page numbers, ensuring a clean final output.

> This stratified approach ensures high precision and recall by combining the explicit structure of numbered lists with the implicit structure of visual typography.

---

## Libraries Utilized

This solution is lightweight and does not utilize any machine learning models, keeping it well under the 200MB size constraint.

- **PyMuPDF (fitz):** A high-performance Python library for PDF parsing. It is used for its speed and its ability to extract detailed text metadata, including content, font names, font sizes, and bounding box coordinates—all of which are essential for our heuristic analysis.
- **collections.Counter:** A standard Python library used to efficiently calculate font and size frequencies to establish the document's baseline style.

---

## How to Build and Run

The solution is fully containerized using Docker and is designed to run completely offline, as per the competition rules.

### Prerequisites

- Docker must be installed and running.

### Step 1: Prepare Directories

Create the required input and output directories in your terminal:

```bash
mkdir -p input/pdfs
mkdir output
```

### Folder layout:

```plaintext
your-working-directory/
├── input/
│   └── pdfs/
│       ├── lecture1.pdf
│       └── notes.pdf
└── output/
```

Place all the PDF files you want to analyze inside the `input/pdfs` folder.

### Step 2: Pull and Run the Docker Container

First, pull the pre-built image from Docker Hub:

```bash
docker pull sidpossibly/round1a-app
```

Next, run the container. This command mounts your local directories into the container and disables networking for a true offline test.

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  --network none \
  sidpossibly/round1a-app
```

---

## Expected Output

For each `yourfile.pdf` in the `input/pdfs/` directory, a corresponding `yourfile.json` will be generated in your `output/` directory, containing the structured document outline.

---

## Authors

- **Deon Sajan** — B.Tech CSE, Amrita Vishwa Vidyapeetham  
- **Sidharth R Krishna** — B.Tech CSE, Amrita Vishwa Vidyapeetham  
- **Yampathi Sai Sailesh Reddy** — B.Tech CSE, Amrita Vishwa Vidyapeetham

---

## Hackathon Submission

**Adobe India – "Connecting the Dots" Challenge 2025**
