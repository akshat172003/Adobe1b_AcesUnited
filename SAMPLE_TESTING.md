# Sample Input/Output for Testing

This document provides sample data and expected outputs to test the Docker setup for the Adobe Challenge 1B PDF Analysis Tool.

## Sample PDF Files

### Creating Test PDFs

You can create sample PDF files for testing using any of these methods:

#### Method 1: Using Python (Recommended)

Create a file `create_sample_pdfs.py`:

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_pdf(filename, content):
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750
    for line in content.split('\n'):
        c.drawString(100, y, line)
        y -= 20
    c.save()

# Sample 1: Academic Research Paper
academic_content = """Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computers to improve their performance on a specific task through experience.

Recent advances in large language models have revolutionized natural language processing. These models, such as GPT-3 and BERT, have demonstrated remarkable capabilities in understanding and generating human-like text.

The field of deep learning has seen significant progress in recent years, with new architectures and training methods being developed regularly. Transformer models have become the foundation for many state-of-the-art NLP systems.

Applications of machine learning span across various domains including healthcare, finance, transportation, and entertainment. The ability to process and analyze large datasets has opened new possibilities for data-driven decision making.

Future directions in machine learning research include improving model interpretability, reducing computational requirements, and addressing ethical concerns related to bias and fairness in AI systems."""

# Sample 2: Technical Documentation
tech_content = """API Documentation for PDF Processing

This document describes the API endpoints for processing PDF documents using semantic analysis techniques.

The main endpoint accepts PDF files and returns structured analysis results including relevance scores and extracted sections.

Authentication is required for all API calls. Use your API key in the Authorization header.

Error handling includes validation of input files, processing timeouts, and memory management for large documents.

Performance considerations include model loading time, memory usage optimization, and concurrent processing capabilities.

The system supports multiple output formats including JSON, XML, and CSV for integration with various downstream applications."""

# Create sample PDFs
create_sample_pdf("sample1.pdf", academic_content)
create_sample_pdf("sample2.pdf", tech_content)
print("Sample PDFs created: sample1.pdf, sample2.pdf")
```

#### Method 2: Using Online Tools

1. Go to https://www.ilovepdf.com/text_to_pdf
2. Create PDFs with the content above
3. Download and rename to `sample1.pdf` and `sample2.pdf`

#### Method 3: Download Sample PDFs

```bash
# Download sample academic papers (if available)
curl -o sample1.pdf "https://example.com/sample-academic-paper.pdf"
curl -o sample2.pdf "https://example.com/sample-tech-doc.pdf"
```

## Expected Output

### Sample Output JSON Structure

When you run the Docker container with the sample PDFs, you should get output similar to this:

```json
{
  "metadata": {
    "input_documents": ["sample1.pdf", "sample2.pdf"],
    "persona": "Academic Researcher in Machine Learning",
    "job-to-be-done": "Survey literature on recent advances in large language models",
    "timestamp": "2024-01-15 14:30:25"
  },
  "extracted_sections": [
    {
      "document": "sample1.pdf",
      "page_number": 1,
      "section_title": "Introduction to Machine Learning",
      "importance_rank": 1
    },
    {
      "document": "sample1.pdf",
      "page_number": 1,
      "section_title": "Recent advances in large language models",
      "importance_rank": 2
    },
    {
      "document": "sample2.pdf",
      "page_number": 1,
      "section_title": "API Documentation for PDF Processing",
      "importance_rank": 3
    }
  ],
  "subsection_analyses": [
    {
      "document": "sample1.pdf",
      "refined_text": "Recent advances in large language models have revolutionized natural language processing.",
      "page_number": 1
    },
    {
      "document": "sample1.pdf",
      "refined_text": "These models, such as GPT-3 and BERT, have demonstrated remarkable capabilities in understanding and generating human-like text.",
      "page_number": 1
    },
    {
      "document": "sample1.pdf",
      "refined_text": "Transformer models have become the foundation for many state-of-the-art NLP systems.",
      "page_number": 1
    }
  ]
}
```

## Testing Steps

### 1. Prepare Test Environment

```bash
# Create input directory
mkdir -p input

# Copy sample PDFs to input folder
cp sample1.pdf input/
cp sample2.pdf input/

# Verify files are in place
ls -la input/
```

### 2. Run Docker Container

```bash
# Build and run using Docker Compose
docker-compose up --build

# Or using Docker commands
docker build -t adobe1b-pdf-analyzer .
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe1b-pdf-analyzer
```

### 3. Verify Results

```bash
# Check output directory
ls -la output/

# View the results
cat output/challenge1b_output.json | python -m json.tool
```

### 4. Expected Log Output

You should see logs similar to:

```
2024-01-15 14:30:20,123 INFO: Use pytorch device_name: cpu
2024-01-15 14:30:20,124 INFO: Load pretrained SentenceTransformer: all-MiniLM-L6-v2
2024-01-15 14:30:25,456 INFO: SentenceTransformer model loaded from all-MiniLM-L6-v2
2024-01-15 14:30:25,457 INFO: Folder already exists: input
2024-01-15 14:30:25,458 INFO: Folder already exists: output
2024-01-15 14:30:25,459 INFO: Found 2 PDF files to process: ['sample1.pdf', 'sample2.pdf']
2024-01-15 14:30:25,460 INFO: Processing complete. Output written to output/challenge1b_output.json.
```

## Performance Testing

### Memory Usage Test

```bash
# Monitor memory usage during processing
docker stats adobe1b-pdf-analyzer
```

### Processing Time Test

```bash
# Time the processing
time docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe1b-pdf-analyzer
```

### Large File Test

Create a larger PDF for stress testing:

```python
# Create a larger test PDF
large_content = "Large Document Test\n" * 1000
create_sample_pdf("large_test.pdf", large_content)
```

## Troubleshooting Test Cases

### Test Case 1: Empty Input Directory

```bash
# Remove all files from input
rm input/*.pdf

# Run container
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe1b-pdf-analyzer

# Expected: Error message about no PDF files found
```

### Test Case 2: Corrupted PDF

```bash
# Create a corrupted PDF
echo "This is not a PDF" > input/corrupted.pdf

# Run container
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe1b-pdf-analyzer

# Expected: Error handling for corrupted file
```

### Test Case 3: Large PDF Files

```bash
# Test with multiple large files
# Expected: Memory management and processing time considerations
```

## Validation Script

Create a validation script `validate_output.py`:

```python
import json
import sys

def validate_output(output_file):
    """Validate the output JSON structure"""
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        # Check required fields
        required_fields = ['metadata', 'extracted_sections', 'subsection_analyses']
        for field in required_fields:
            if field not in data:
                print(f"ERROR: Missing required field '{field}'")
                return False
        
        # Check metadata
        metadata = data['metadata']
        required_metadata = ['input_documents', 'persona', 'job-to-be-done', 'timestamp']
        for field in required_metadata:
            if field not in metadata:
                print(f"ERROR: Missing metadata field '{field}'")
                return False
        
        print("✅ Output validation passed!")
        print(f"📊 Found {len(data['extracted_sections'])} extracted sections")
        print(f"🔍 Found {len(data['subsection_analyses'])} subsection analyses")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to validate output: {e}")
        return False

if __name__ == "__main__":
    output_file = "output/challenge1b_output.json"
    success = validate_output(output_file)
    sys.exit(0 if success else 1)
```

Run validation:

```bash
python validate_output.py
```

## Automated Testing

Create a test script `run_tests.py`:

```python
import subprocess
import os
import json

def run_docker_test():
    """Run automated Docker tests"""
    print("🚀 Starting Docker tests...")
    
    # Clean up previous test results
    if os.path.exists("output/challenge1b_output.json"):
        os.remove("output/challenge1b_output.json")
    
    # Run Docker container
    result = subprocess.run([
        "docker", "run", 
        "-v", f"{os.getcwd()}/input:/app/input",
        "-v", f"{os.getcwd()}/output:/app/output",
        "adobe1b-pdf-analyzer"
    ], capture_output=True, text=True)
    
    # Check if output was created
    if os.path.exists("output/challenge1b_output.json"):
        print("✅ Output file created successfully")
        
        # Validate output
        with open("output/challenge1b_output.json", 'r') as f:
            data = json.load(f)
        
        print(f"📊 Processed {len(data.get('extracted_sections', []))} sections")
        print(f"🔍 Found {len(data.get('subsection_analyses', []))} relevant subsections")
        
        return True
    else:
        print("❌ Output file not created")
        print(f"Container logs: {result.stdout}")
        print(f"Container errors: {result.stderr}")
        return False

if __name__ == "__main__":
    success = run_docker_test()
    exit(0 if success else 1)
```

Run automated tests:

```bash
python run_tests.py
``` 