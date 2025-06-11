"""Integration tests for the PDFProcessor class."""
import pytest
from pathlib import Path
import json
from app.services.pdf_processor import PDFProcessor

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

@pytest.fixture
def sample_pdf_path():
    return Path(__file__).parent.parent.parent / "lekl101.pdf"

def test_complete_pdf_processing_workflow(pdf_processor, sample_pdf_path, tmp_path):
    """Test the complete workflow of processing a PDF and saving results."""
    
    # 1. Process the PDF
    result = pdf_processor.process_pdf(sample_pdf_path)
    
    # 2. Verify the structure and content
    assert "metadata" in result
    assert "chunks" in result
    assert "document_info" in result
    assert "people_mentioned" in result
    
    # 3. Check metadata
    metadata = result["metadata"]
    assert metadata["file_name"] == "lekl101.pdf"
    assert metadata["file_size"] > 0
    assert metadata["page_count"] > 0
    
    # 4. Check chunks
    chunks = result["chunks"]
    assert len(chunks) > 0
    for chunk in chunks:
        assert "content" in chunk
        assert "chunk_metadata" in chunk
        assert isinstance(chunk["content"], str)
        assert len(chunk["content"]) > 0
    
    # 5. Check document info
    doc_info = result["document_info"]
    assert doc_info["filename"] == "lekl101.pdf"
    assert doc_info["total_pages"] > 0
    assert doc_info["total_chunks"] == len(chunks)
    assert doc_info["file_size_bytes"] > 0
    
    # 6. Test saving to JSON
    output_path = tmp_path / "processed_pdf.json"
    pdf_processor.save_to_json(result, output_path)
    
    # 7. Verify saved JSON
    assert output_path.exists()
    with open(output_path, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    
    # 8. Compare saved data with original result
    assert saved_data == result
    
    # 9. Check chunk content characteristics
    total_text = ""
    for chunk in chunks:
        chunk_text = chunk["content"]
        # Verify chunk size is within expected range
        assert len(chunk_text) <= pdf_processor.chunk_size + pdf_processor.chunk_overlap
        total_text += chunk_text
    
    # 10. Verify total content is substantial
    assert len(total_text) > 0
    
    # 11. Check for names in the content
    if result["people_mentioned"]:
        # If any names were found, verify they appear in the text
        for name in result["people_mentioned"]:
            assert name.lower() in total_text.lower()

def test_error_handling_and_logging(pdf_processor, sample_pdf_path, tmp_path):
    """Test error handling and logging for various scenarios."""
    
    # 1. Test with non-existent file
    with pytest.raises(FileNotFoundError):
        pdf_processor.process_pdf(tmp_path / "nonexistent.pdf")
    
    # 2. Test with invalid save path
    result = pdf_processor.process_pdf(sample_pdf_path)
    with pytest.raises(Exception):
        pdf_processor.save_to_json(result, "/invalid/path/output.json")
