"""Text cleaning utilities for RAG processing"""
import re


def clean_text_for_rag(text: str) -> str:
    """Clean and normalize text for RAG processing"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove page numbers (common patterns)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    text = re.sub(r'\n\s*[-–—]\s*\d+\s*[-–—]\s*\n', '\n', text)
    
    # Remove headers/footers (repeated text at top/bottom)
    lines = text.split('\n')
    if len(lines) > 10:
        # Simple heuristic: remove identical lines appearing frequently
        line_counts = {}
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) > 10:
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        repeated = {line for line, count in line_counts.items() if count > 3}
        lines = [line for line in lines if line.strip() not in repeated]
        text = '\n'.join(lines)
    
    # Fix hyphenated line breaks
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Remove excessive whitespace while preserving paragraph breaks
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
    
    # Remove standalone special characters and artifacts
    text = re.sub(r'\n[•●○■□▪▫‣⁃]+\s*\n', '\n', text)
    text = re.sub(r'[▪▫■□●○•]{2,}', '', text)
    
    text = re.sub(r'[^\S\n]+\n', '\n', text)  # Remove trailing whitespace
    text = re.sub(r'\n[^\S\n]+', '\n', text)  # Remove leading whitespace
    
    # Remove non-printable characters except newlines and tabs
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    # Normalize unicode characters
    replacements = {
        '\u2018': "'", '\u2019': "'",  # Smart quotes
        '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-',  # En/em dashes
        '\u2026': '...',  # Ellipsis
        '\xa0': ' ',  # Non-breaking space
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Clean up artifacts from tables
    text = re.sub(r'\|+', ' ', text)  # Remove table borders
    text = re.sub(r'_{3,}', '', text)  # Remove underline sequences
    
    # Final cleanup
    text = text.strip()
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    
    return text
