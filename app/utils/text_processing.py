import re
from typing import List

def clean_text(text: str) -> str:
    """
    Clean and normalize text from PDF
    
    Args:
        text: Raw text extracted from PDF
    
    Returns:
        Cleaned and normalized text
    """
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove hyphenation at end of lines
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    # Fix common PDF extraction issues
    text = re.sub(r'([a-z])- ([a-z])', r'\1\2', text)  # Fix wrong hyphenation
    text = re.sub(r'\f', ' ', text)  # Remove form feeds
    
    # Remove multiple newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()

def is_chapter_header(text: str) -> bool:
    """
    Check if a text line is likely a chapter header
    
    Args:
        text: Line of text to check
    
    Returns:
        True if line appears to be a chapter header
    """
    chapter_patterns = [
        r'^chapter\s+\d+',
        r'^chapter\s+[ivxlcdm]+',
    ]
    
    text = text.lower().strip()
    return any(re.match(pattern, text) for pattern in chapter_patterns)

def extract_metadata(text: str, page_num: int) -> dict:
    """
    Extract metadata from text chunk
    
    Args:
        text: Text chunk
        page_num: Page number
    
    Returns:
        Dictionary with metadata
    """
    metadata = {
        "page_number": page_num,
        "is_chapter_start": is_chapter_header(text.split('\n')[0]),
        "character_mentions": extract_character_mentions(text),
    }
    return metadata

def extract_character_mentions(text: str) -> List[str]:
    """
    Extract main character names mentioned in text
    
    Args:
        text: Text to analyze
    
    Returns:
        List of character names found
    """
    main_characters = [
        "Harry", "Potter", "Ron", "Weasley",
        "Hermione", "Granger", "Draco", "Malfoy",
        "Dumbledore", "Snape", "McGonagall", "Hagrid"
    ]
    
    mentions = []
    for character in main_characters:
        if character.lower() in text.lower():
            mentions.append(character)
            
    return list(set(mentions))
