# Adobe Challenge 1B - PDF Document Analysis

A Python script for intelligent PDF document analysis using semantic similarity and machine learning. This tool extracts relevant sections from PDF documents based on a specified persona and job-to-be-done.

## Features

- **Automatic PDF Processing**: Extracts text sections from PDF documents
- **Semantic Analysis**: Uses SentenceTransformer for intelligent text relevance scoring
- **Persona-Based Filtering**: Ranks content based on specific user personas and tasks
- **Subsection Analysis**: Further breaks down relevant sections for detailed insights
- **Automatic Folder Management**: Creates input/output folders as needed
- **Robust Error Handling**: Graceful handling of missing files and processing errors

## Requirements

- Python 3.7+
- PyPDF2
- sentence-transformers
- numpy

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd adobe_1b
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

1. **Place your PDF files** in the `input` folder (or in the current directory)
2. **Run the script**:
```bash
python script.py
```
3. **Check results** in the `output` folder

### Configuration

You can modify the following parameters in `script.py`:

```python
# PDF files to process (place these in input folder or current directory)
pdfs = ['sample1.pdf', 'sample2.pdf']

# Persona and job description
persona = "Academic Researcher in Machine Learning"
job = "Survey literature on recent advances in large language models"

# Output filename
output_json = "challenge1b_output.json"
```

### Input/Output Structure

```
adobe_1b/
├── input/          # Place your PDF files here
├── output/         # Generated results
├── script.py       # Main processing script
├── requirements.txt # Dependencies
└── README.md       # This file
```

## How It Works

1. **PDF Extraction**: Extracts text sections from PDF documents using PyPDF2
2. **Semantic Embedding**: Converts text sections to vector embeddings using SentenceTransformer
3. **Relevance Scoring**: Computes cosine similarity between sections and the persona/job query
4. **Ranking**: Ranks sections by relevance score
5. **Subsection Analysis**: Further analyzes relevant sections for detailed insights
6. **Output Generation**: Saves results as structured JSON

## Output Format

The script generates a JSON file with the following structure:

```json
{
  "metadata": {
    "input_documents": ["document1.pdf", "document2.pdf"],
    "persona": "Academic Researcher in Machine Learning",
    "job-to-be-done": "Survey literature on recent advances in large language models",
    "timestamp": "2024-01-01 12:00:00"
  },
  "extracted_sections": [
    {
      "document": "document1.pdf",
      "page_number": 1,
      "section_title": "Introduction",
      "importance_rank": 1
    }
  ],
  "subsection_analyses": [
    {
      "document": "document1.pdf",
      "refined_text": "Specific relevant text snippet",
      "page_number": 1
    }
  ]
}
```

## Error Handling

The script includes comprehensive error handling for:
- Missing PDF files
- Corrupted PDF documents
- Model loading issues
- File system errors
- Processing failures

## Model Information

- **Model**: `all-MiniLM-L6-v2` (SentenceTransformer)
- **Size**: <1GB
- **Features**: 384-dimensional embeddings
- **Use Case**: Semantic similarity for text relevance scoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Adobe Challenge 1B submission.

## Troubleshooting

### Common Issues

1. **No PDF files found**: Ensure PDF files are in the `input` folder or current directory
2. **Model loading error**: Check internet connection for first-time model download
3. **Memory issues**: The model requires ~1GB RAM for processing

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Ensure all dependencies are installed
3. Verify PDF files are accessible and not corrupted 