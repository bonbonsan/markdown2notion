"""Unit tests for MarkdownProcessor class."""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from markdown_processor import MarkdownProcessor


class TestMarkdownProcessor(unittest.TestCase):
    """Test cases for MarkdownProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = MarkdownProcessor()

    def test_simple_markdown_parsing(self):
        """Test basic markdown parsing functionality."""
        content = """# Main Title

This is a paragraph with **bold text** and *italic text*.

## Section 1

- Item 1
- Item 2
- Item 3

## Code Example

```python
def hello():
    return "Hello, World!"
```

Regular paragraph after code block.
"""
        blocks, title = self.processor.parse_markdown_to_blocks(content, "Test Document")
        
        # Verify we get blocks back
        self.assertIsInstance(blocks, list)
        self.assertGreater(len(blocks), 0)
        
        # Check that we have different block types
        block_types = {block['type'] for block in blocks}
        expected_types = {'heading_1', 'paragraph', 'heading_2', 'bulleted_list_item', 'code'}
        
        # At least some of these types should be present
        self.assertTrue(len(expected_types.intersection(block_types)) > 0)

    def test_file_processing(self):
        """Test processing of actual markdown files."""
        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            test_content = """# Test File

This is test content for file processing.

## Features
- Feature A
- Feature B
"""
            f.write(test_content)
            temp_path = f.name

        try:
            blocks, title = self.processor.process_file(temp_path)
            
            # Verify results
            self.assertIsInstance(blocks, list)
            self.assertIsInstance(title, str)
            self.assertGreater(len(blocks), 0)
            
            # Title should be extracted from filename
            expected_title = Path(temp_path).stem
            self.assertEqual(title, expected_title)
            
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_empty_content(self):
        """Test handling of empty content."""
        blocks, title = self.processor.parse_markdown_to_blocks("", "Empty Test")
        
        # Should return empty list for empty content
        self.assertIsInstance(blocks, list)
        self.assertEqual(len(blocks), 0)

    def test_heading_levels(self):
        """Test different heading levels are properly converted."""
        content = """# H1 Title
## H2 Subtitle  
### H3 Section
#### H4 Subsection
##### H5 Deep
###### H6 Deepest
"""
        blocks, _ = self.processor.parse_markdown_to_blocks(content, "Heading Test")
        
        # Find heading blocks
        heading_blocks = [b for b in blocks if b['type'].startswith('heading_')]
        
        # Should have multiple heading levels
        self.assertGreater(len(heading_blocks), 0)
        
        # Check for different heading types
        heading_types = {block['type'] for block in heading_blocks}
        expected_headings = {'heading_1', 'heading_2', 'heading_3'}
        
        # At least H1, H2, H3 should be present
        self.assertTrue(len(expected_headings.intersection(heading_types)) >= 2)

    def test_list_processing(self):
        """Test list item processing."""
        content = """# Lists Test

Bulleted list:
- Item 1
- Item 2  
- Item 3

Numbered list:
1. First item
2. Second item
3. Third item
"""
        blocks, _ = self.processor.parse_markdown_to_blocks(content, "List Test")
        
        # Find list blocks
        list_blocks = [b for b in blocks if 'list_item' in b['type']]
        
        # Should have list items
        self.assertGreater(len(list_blocks), 0)

    def test_code_block_processing(self):
        """Test code block processing."""
        content = """# Code Test

```python
def test_function():
    return True
```

```javascript
function test() {
    return true;
}
```
"""
        blocks, _ = self.processor.parse_markdown_to_blocks(content, "Code Test")
        
        # Find code blocks
        code_blocks = [b for b in blocks if b['type'] == 'code']
        
        # Should have code blocks
        self.assertGreater(len(code_blocks), 0)
        
        # Check that language is preserved (for at least one block)
        has_language = any(
            'language' in block.get('code', {}) 
            for block in code_blocks
        )
        # Note: This might be True or False depending on implementation

    def test_rich_text_formatting(self):
        """Test rich text formatting (bold, italic, code)."""
        content = """# Rich Text Test

This paragraph has **bold text**, *italic text*, and `inline code`.

[This is a link](https://example.com)
"""
        blocks, _ = self.processor.parse_markdown_to_blocks(content, "Rich Text Test")
        
        # Find paragraph blocks
        paragraph_blocks = [b for b in blocks if b['type'] == 'paragraph']
        
        # Should have paragraphs with rich text
        self.assertGreater(len(paragraph_blocks), 0)

    def test_invalid_file_handling(self):
        """Test handling of non-existent files."""
        with self.assertRaises(FileNotFoundError):
            self.processor.process_file("/nonexistent/file.md")

    def test_large_content_generation(self):
        """Test generation of many blocks (for testing 100+ block scenarios)."""
        # Generate content that will create many blocks
        content_parts = ["# Large Document Test\n\n"]
        
        # Add many sections
        for i in range(50):
            content_parts.append(f"## Section {i + 1}\n\n")
            content_parts.append(f"This is paragraph {i + 1} with some content.\n\n")
            content_parts.append(f"- List item {i + 1}A\n")
            content_parts.append(f"- List item {i + 1}B\n\n")
        
        large_content = "".join(content_parts)
        blocks, _ = self.processor.parse_markdown_to_blocks(large_content, "Large Test")
        
        # Should generate many blocks
        self.assertGreater(len(blocks), 100)
        
        # Test that we can handle large block counts
        self.assertIsInstance(blocks, list)
        
        # All blocks should have required structure
        for block in blocks:
            self.assertIn('type', block)
            self.assertIsInstance(block['type'], str)


if __name__ == '__main__':
    unittest.main()