"""
Markdown processor module for converting Markdown to Notion blocks.
Handles parsing of Markdown files and conversion to Notion API format.
"""

import re
from typing import List, Dict, Any, Tuple
from pathlib import Path


class MarkdownProcessor:
    """
    Processes Markdown content and converts it to Notion block format.
    Uses filename as page title instead of H1 tags.
    """

    def __init__(self):
        """Initialize the MarkdownProcessor."""
        pass

    def extract_title_from_filepath(self, filepath: str) -> str:
        """
        Extract page title from file path by using the filename without extension.
        
        Args:
            filepath: Path to the Markdown file
            
        Returns:
            The filename without extension as page title
        """
        path_obj = Path(filepath)
        return path_obj.stem

    def parse_markdown_to_blocks(self, markdown_content: str, title: str = "") -> Tuple[List[Dict[str, Any]], str]:
        """
        Parse Markdown content and convert to Notion blocks.
        
        Args:
            markdown_content: The Markdown content to parse
            title: The page title (from filename)
            
        Returns:
            Tuple of (blocks list, title)
        """
        lines = markdown_content.strip().split('\n')
        blocks = []
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Handle headings (H1-H6) - all treated as content, not page title
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 6:
                    heading_text = line[level:].strip()
                    
                    if level == 1:
                        block_type = "heading_1"
                        block_key = "heading_1"
                    elif level == 2:
                        block_type = "heading_2"
                        block_key = "heading_2"
                    elif level == 3:
                        block_type = "heading_3"
                        block_key = "heading_3"
                    else:
                        # For H4-H6, use H3 format in Notion
                        block_type = "heading_3"
                        block_key = "heading_3"
                        heading_text = f"{'#' * (level - 3)} {heading_text}"
                    
                    blocks.append({
                        "type": block_type,
                        block_key: {
                            "rich_text": [{"type": "text", "text": {"content": heading_text}}]
                        }
                    })
                    i += 1
                    continue
            
            # Handle code blocks
            if line.startswith('```'):
                language = line[3:].strip() or "plain text"
                code_lines = []
                i += 1
                
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if i < len(lines):  # Skip the closing ```
                    i += 1
                
                code_content = '\n'.join(code_lines)
                blocks.append({
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": code_content}}],
                        "language": language
                    }
                })
                continue
            
            # Handle bulleted lists
            if line.startswith('- ') or line.startswith('* '):
                content = line[2:].strip()
                blocks.append({
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                })
                i += 1
                continue
            
            # Handle numbered lists
            numbered_match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if numbered_match:
                content = numbered_match.group(2)
                blocks.append({
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                })
                i += 1
                continue
            
            # Handle blockquotes
            if line.startswith('> '):
                content = line[2:].strip()
                blocks.append({
                    "type": "quote",
                    "quote": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                })
                i += 1
                continue
            
            # Handle todo items
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                checked = line.startswith('- [x]')
                content = line[5:].strip()
                blocks.append({
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": content}}],
                        "checked": checked
                    }
                })
                i += 1
                continue
            
            # Handle regular paragraphs
            # Collect consecutive non-empty lines as a single paragraph
            paragraph_lines = []
            while i < len(lines):
                current_line = lines[i].rstrip()
                if (not current_line or 
                    current_line.startswith('#') or 
                    current_line.startswith('```') or 
                    current_line.startswith('- ') or 
                    current_line.startswith('* ') or 
                    current_line.startswith('> ') or
                    re.match(r'^\d+\.\s+', current_line)):
                    break
                paragraph_lines.append(current_line)
                i += 1
            
            if paragraph_lines:
                paragraph_content = ' '.join(line for line in paragraph_lines if line)
                if paragraph_content:
                    blocks.append({
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": paragraph_content}}]
                        }
                    })
            
        return blocks, title

    def process_file(self, filepath: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Process a Markdown file and return Notion blocks and title.
        
        Args:
            filepath: Path to the Markdown file
            
        Returns:
            Tuple of (blocks list, page title from filename)
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path_obj = Path(filepath)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Extract title from filename
        title = self.extract_title_from_filepath(filepath)
        
        # Read and process file content
        with open(path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks, _ = self.parse_markdown_to_blocks(content, title)
        return blocks, title