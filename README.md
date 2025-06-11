# PDF Processing and Analysis Tool

A powerful Python-based tool for processing and analyzing PDF documents. This tool combines the capabilities of LangChain for document processing, spaCy for Natural Language Processing, and PDFMiner for detailed metadata extraction.

## Key Features

- PDF text extraction with metadata
- Recursive character text chunking
- Named Entity Recognition for identifying people mentioned in the text
- Detailed metadata extraction (creation date, modification date, file size, etc.)
- Configurable chunk sizes and overlap
- JSON export capabilities
- Comprehensive error handling

## Prerequisites

- Python 3.10 or higher
- pip package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AskHogwarts
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
.\venv\Scripts\activate  # On Windows
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Install the spaCy English language model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

Here's a basic example of how to use the PDF processor:

```python
from app.services.pdf_processor import PDFProcessor
from pathlib import Path

# Initialize the processor
processor = PDFProcessor(
    chunk_size=1000,  # Size of text chunks
    chunk_overlap=200  # Overlap between chunks
)

# Process a PDF file
pdf_path = Path("path/to/your/document.pdf")
result = processor.process_pdf(pdf_path)

# Save the results to JSON
processor.save_to_json(result, "output.json")
```

### Output Structure

The processor returns a dictionary with the following structure:

```json
{
    "metadata": {
        "file_name": "example.pdf",
        "file_size": 12345,
        "page_count": 10,
        "created_date": "...",
        "modified_date": "..."
    },
    "chunks": [
        {
            "content": "...",
            "chunk_metadata": {},
            "chunk_id": "chunk_0",
            "word_count": 150,
            "char_count": 800
        }
    ],
    "document_info": {
        "total_pages": 10,
        "filename": "example.pdf",
        "total_chunks": 5,
        "file_size_bytes": 12345
    },
    "people_mentioned": ["john smith", "jane doe"],
    "processing_info": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "processing_date": "2025-06-12T10:00:00",
        "processor_version": "1.0.0"
    }
}
```

## Configuration

The PDFProcessor class accepts several configuration options:

```python
processor = PDFProcessor(
    chunk_size=1000,          # Size of text chunks (in characters)
    chunk_overlap=200,        # Overlap between chunks
    min_chunk_size=100,       # Minimum chunk size
    spacy_model="en_core_web_sm",  # spaCy model for NER
    enable_logging=True       # Enable detailed logging
)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| chunk_size | int | 1000 | The target size for text chunks |
| chunk_overlap | int | 200 | Number of characters to overlap between chunks |
| min_chunk_size | int | 100 | Minimum size for a valid chunk |
| spacy_model | str | "en_core_web_sm" | The spaCy model to use for NER |
| enable_logging | bool | True | Enable/disable detailed logging |

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with verbose output
python -m pytest -v tests/

# Run with coverage report
python -m pytest --cov=app tests/
```

## Advanced Usage

### Batch Processing

Process multiple PDF files:

```python
from app.services.pdf_processor import PDFProcessor
from pathlib import Path

processor = PDFProcessor()
pdf_directory = Path("path/to/pdf/directory")
results = []

for pdf_file in pdf_directory.glob("*.pdf"):
    try:
        result = processor.process_pdf(pdf_file)
        results.append(result)
    except Exception as e:
        print(f"Error processing {pdf_file}: {str(e)}")
```

### Custom NER Configuration

Configure custom NER settings:

```python
from app.services.pdf_processor import PDFProcessor
import spacy

# Load a custom spaCy model
nlp = spacy.load("en_core_web_lg")  # Using the larger model

processor = PDFProcessor(spacy_model=nlp)
```

## Troubleshooting

### Common Issues

1. **PDFMiner Errors**
   - Ensure the PDF is not password-protected
   - Check if the PDF is corrupted
   - Try with a different PDF to isolate the issue

2. **Memory Issues**
   - Reduce chunk_size for large documents
   - Process large PDFs in sections
   - Monitor system memory usage

3. **spaCy Model Issues**
   - Ensure the model is properly installed
   - Try downloading the model again
   - Check spaCy compatibility with Python version

### Error Messages

| Error | Possible Cause | Solution |
|-------|---------------|----------|
| `PDFSyntaxError` | Corrupted PDF | Try redownloading or repairing the PDF |
| `MemoryError` | PDF too large | Reduce chunk size or process in sections |
| `ModuleNotFoundError` | Missing dependencies | Check requirements.txt and reinstall |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain for document processing capabilities
- spaCy for excellent NLP capabilities
- PDFMiner for reliable PDF text extraction
