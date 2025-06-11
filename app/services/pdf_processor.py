"""
PDF Processing module with recursive character text chunking capabilities and enhanced metadata extraction.
"""
from typing import Dict, List, Optional, Set
from pathlib import Path
import json
import re
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader, PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger
import spacy
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("Downloading spaCy model...")
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


class PDFProcessor:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = ["\n\n", "\n", " ", ""],
    ):
        """
        Initialize the PDF processor with chunking parameters.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            separators: List of separators for text splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
        )
        
    def extract_detailed_metadata(self, pdf_path: Path) -> Dict:
        """
        Extract detailed metadata from PDF using PDFMiner.
        """
        with open(pdf_path, 'rb') as file:
            parser = PDFParser(file)
            doc = PDFDocument(parser)
            
            metadata = {}
            
            if doc.info:
                # Extract standard PDF metadata
                for key, value in doc.info[0].items():
                    try:
                        # Decode binary string metadata
                        if isinstance(value, bytes):
                            value = value.decode('utf-8', errors='ignore')
                        metadata[key.decode('utf-8').lower()] = value
                    except Exception as e:
                        logger.warning(f"Could not decode metadata {key}: {e}")
            
            # Add document properties
            metadata.update({
                "page_count": sum(1 for _ in PDFPage.create_pages(doc)),
                "file_name": pdf_path.name,
                "file_size": pdf_path.stat().st_size,
                "created_date": metadata.get("creationdate", ""),
                "modified_date": metadata.get("moddate", ""),
            })
            
            return metadata
            
    def extract_people_names(self, text: str) -> Set[str]:
        """
        Extract people's names from text using spaCy NER.
        Returns lowercase names for consistency.
        """
        doc = nlp(text)
        names = set()
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.add(ent.text.lower())
                
        return names

    def process_pdf(self, pdf_path: str | Path) -> Dict:
        """
        Process a PDF file and return its content in structured format.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict containing processed PDF data including:
            - metadata
            - chunks
            - document_info
            - people_mentioned
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            logger.info(f"Processing PDF: {pdf_path}")
            
            # Get detailed metadata
            metadata = self.extract_detailed_metadata(pdf_path)
            
            # Load and process content
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            
            # Process all pages and create chunks
            all_text = "\n".join(page.page_content for page in pages)
            chunks = self.text_splitter.create_documents([all_text])
            
            # Extract people's names
            people_mentioned = self.extract_people_names(all_text)
            
            # Prepare the document info
            document_info = {
                "total_pages": len(pages),
                "filename": pdf_path.name,
                "total_chunks": len(chunks),
                "file_size_bytes": metadata["file_size"],
                "created_date": metadata.get("created_date", ""),
                "modified_date": metadata.get("modified_date", ""),
            }

            # Create the result dictionary with enhanced schema
            result = {
                "metadata": {
                    **metadata,
                    "total_word_count": sum(len(chunk.page_content.split()) for chunk in chunks),
                    "total_char_count": sum(len(chunk.page_content) for chunk in chunks),
                    "average_chunk_size": sum(len(chunk.page_content) for chunk in chunks) / len(chunks),
                    "language_detected": "en",  # We could add language detection here
                    "processing_timestamp": datetime.now().isoformat(),
                    "total_people_mentioned": len(people_mentioned),
                    "document_statistics": {
                        "pages": len(pages),
                        "chunks": len(chunks),
                        "file_size_bytes": metadata["file_size"],
                        "avg_words_per_chunk": sum(len(chunk.page_content.split()) for chunk in chunks) / len(chunks)
                    }
                },
                "chunks": [
                    {
                        "content": chunk.page_content,
                        "chunk_metadata": {
                            "chunk_id": f"chunk_{i}",
                            "page_number": i // (len(chunks) // len(pages)) + 1,
                            "word_count": len(chunk.page_content.split()),
                            "char_count": len(chunk.page_content),
                            "chunk_position": {
                                "index": i,
                                "total_chunks": len(chunks)
                            },
                            "people_mentioned": [
                                name for name in people_mentioned 
                                if name.lower() in chunk.page_content.lower()
                            ],
                            "chunk_size_bytes": len(chunk.page_content.encode('utf-8')),
                            "overlap_with_next": self.chunk_overlap if i < len(chunks) - 1 else 0,
                            "processing_info": {
                                "chunk_method": "recursive_character",
                                "chunk_size": self.chunk_size,
                                "chunk_overlap": self.chunk_overlap
                            }
                        },
                        "chunk_id": f"chunk_{i}",
                        "word_count": len(chunk.page_content.split()),
                        "char_count": len(chunk.page_content)
                    }
                    for i, chunk in enumerate(chunks)
                ],
                "document_info": document_info,
                "people_mentioned": list(people_mentioned),
                "processing_info": {
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "processing_date": datetime.now().isoformat(),
                    "processor_version": "1.0.0"
                }
            }

            return result

        except FileNotFoundError as e:
            logger.error(f"PDF file not found: {pdf_path}")
            raise
        except Exception as e:
            if "EOF marker not found" in str(e) or "syntax error" in str(e).lower():
                logger.error(f"Invalid or corrupted PDF file {pdf_path}: {str(e)}")
                raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise

    def save_to_json(self, data: Dict, output_path: str | Path) -> None:
        """
        Save the processed PDF data to a JSON file.
        
        Args:
            data: Processed PDF data dictionary
            output_path: Path where to save the JSON file
        
        Raises:
            OSError: If there are permission issues or other IO problems
            TypeError: If the data cannot be serialized to JSON
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Validate data structure before saving
            required_keys = {"metadata", "chunks", "document_info", "people_mentioned", "processing_info"}
            if not all(key in data for key in required_keys):
                raise ValueError("Invalid data structure: missing required keys")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved processed data to {output_path}")
            
        except (OSError, TypeError) as e:
            logger.error(f"Error saving to JSON: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while saving to JSON: {str(e)}")
            raise
