"""Unit tests for the PDFProcessor class."""
import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

@pytest.fixture
def sample_pdf_path():
    # Use the leki101.pdf from the project root
    return Path(__file__).parent.parent.parent / "lekl101.pdf"

def test_pdf_processor_initialization(pdf_processor):
    """Test PDFProcessor initialization with default parameters."""
    assert pdf_processor.chunk_size == 1000
    assert pdf_processor.chunk_overlap == 200
    assert pdf_processor.separators == ["\n\n", "\n", " ", ""]

def test_pdf_processor_with_custom_params():
    """Test PDFProcessor initialization with custom parameters."""
    processor = PDFProcessor(chunk_size=500, chunk_overlap=100)
    assert processor.chunk_size == 500
    assert processor.chunk_overlap == 100

def test_extract_detailed_metadata(pdf_processor, sample_pdf_path):
    """Test metadata extraction from PDF."""
    metadata = pdf_processor.extract_detailed_metadata(sample_pdf_path)
    
    # Basic metadata checks
    assert isinstance(metadata, dict)
    assert "file_name" in metadata
    assert "file_size" in metadata
    assert "page_count" in metadata
    assert metadata["file_name"] == "lekl101.pdf"
    assert metadata["file_size"] > 0
    assert metadata["page_count"] > 0

def test_extract_people_names(pdf_processor):
    """Test people name extraction from text."""
    sample_text = "John Smith and Mary Johnson went to the store. Barack Obama was president."
    names = pdf_processor.extract_people_names(sample_text)
    
    assert isinstance(names, set)
    assert "john smith" in names
    assert "mary johnson" in names
    assert "barack obama" in names

def test_process_pdf(pdf_processor, sample_pdf_path):
    """Test complete PDF processing."""
    result = pdf_processor.process_pdf(sample_pdf_path)
    
    # Check structure
    assert isinstance(result, dict)
    assert "metadata" in result
    assert "chunks" in result
    assert "document_info" in result
    assert "people_mentioned" in result
    
    # Check chunks
    assert len(result["chunks"]) > 0
    assert isinstance(result["chunks"], list)
    
    # Check document info
    doc_info = result["document_info"]
    assert doc_info["filename"] == "lekl101.pdf"
    assert doc_info["total_pages"] > 0
    assert doc_info["total_chunks"] > 0
    assert doc_info["file_size_bytes"] > 0

def test_process_nonexistent_pdf(pdf_processor):
    """Test handling of non-existent PDF file."""
    with pytest.raises(FileNotFoundError):
        pdf_processor.process_pdf("nonexistent.pdf")
