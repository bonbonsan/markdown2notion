"""Unit tests for NotionUploader class."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile
import os

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notion_uploader import NotionUploader


class TestNotionUploader(unittest.TestCase):
    """Test cases for NotionUploader."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the Notion client to avoid real API calls
        with patch('notion_uploader.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock environment variables
            with patch.dict('os.environ', {'NOTION_TOKEN': 'test_token'}):
                self.uploader = NotionUploader()
                self.mock_client = mock_client

    def test_initialization_with_token(self):
        """Test NotionUploader initialization with provided token."""
        with patch('notion_uploader.Client') as mock_client_class:
            uploader = NotionUploader(token="test_token_direct")
            mock_client_class.assert_called_once_with(auth="test_token_direct")

    def test_initialization_without_token_raises_error(self):
        """Test that missing token raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('notion_uploader.load_dotenv'):
                with self.assertRaises(ValueError) as context:
                    NotionUploader()
                
                self.assertIn("NOTION_TOKEN is required", str(context.exception))

    def test_extract_page_id_from_url_standard_format(self):
        """Test URL parsing for standard Notion URLs."""
        test_cases = [
            (
                "https://www.notion.so/My-Page-16132a3709e4816cb512e4d73d345003",
                "16132a37-09e4-816c-b512-e4d73d345003"
            ),
            (
                "https://notion.so/16132a3709e4816cb512e4d73d345003",
                "16132a37-09e4-816c-b512-e4d73d345003"
            ),
            (
                "https://workspace.notion.site/Page-Title-16132a3709e4816cb512e4d73d345003",
                "16132a37-09e4-816c-b512-e4d73d345003"
            )
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                result = NotionUploader.extract_page_id_from_url(url)
                self.assertEqual(result, expected_id)

    def test_extract_page_id_from_url_invalid_format(self):
        """Test URL parsing with invalid URLs."""
        invalid_urls = [
            "https://invalid-url.com",
            "not-a-url",
            "https://notion.so/invalid",
            "https://notion.so/tooshort123",
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError) as context:
                    NotionUploader.extract_page_id_from_url(url)
                
                self.assertIn("Invalid Notion URL format", str(context.exception))

    def test_create_page_with_blocks_small_file(self):
        """Test page creation with <= 100 blocks."""
        # Mock blocks (small number)
        test_blocks = [
            {"type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Test"}}]}},
            {"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Content"}}]}}
        ]
        
        # Mock successful page creation
        mock_page_response = {"id": "test-page-id-123"}
        self.mock_client.pages.create.return_value = mock_page_response
        
        result = self.uploader._create_page_with_blocks(
            blocks=test_blocks,
            title="Test Page",
            parent_page_id="parent-id"
        )
        
        # Verify single API call for small files
        self.mock_client.pages.create.assert_called_once()
        self.assertEqual(result, "test-page-id-123")
        
        # Should not call blocks.children.append for small files
        self.mock_client.blocks.children.append.assert_not_called()

    def test_create_page_with_blocks_large_file(self):
        """Test page creation with > 100 blocks."""
        # Create 150 test blocks
        test_blocks = []
        for i in range(150):
            test_blocks.append({
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": f"Paragraph {i}"}}]}
            })
        
        # Mock successful page creation
        mock_page_response = {"id": "test-page-id-456"}
        self.mock_client.pages.create.return_value = mock_page_response
        
        result = self.uploader._create_page_with_blocks(
            blocks=test_blocks,
            title="Large Test Page",
            parent_page_id="parent-id"
        )
        
        # Verify initial page creation with first 100 blocks
        self.mock_client.pages.create.assert_called_once()
        call_args = self.mock_client.pages.create.call_args
        
        # Check that only first 100 blocks were used in initial creation
        children_blocks = call_args[1]['children']
        self.assertEqual(len(children_blocks), 100)
        
        # Verify additional blocks were appended
        self.mock_client.blocks.children.append.assert_called_once()
        append_call_args = self.mock_client.blocks.children.append.call_args
        
        # Check that remaining 50 blocks were appended
        appended_blocks = append_call_args[1]['children']
        self.assertEqual(len(appended_blocks), 50)
        
        self.assertEqual(result, "test-page-id-456")

    @patch('notion_uploader.MarkdownProcessor')
    def test_upload_markdown_file_with_parent_url(self, mock_processor_class):
        """Test file upload using parent URL."""
        # Setup mocks
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_file.return_value = (
            [{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "test"}}]}}],
            "Test Title"
        )
        
        mock_page_response = {"id": "new-page-id"}
        self.mock_client.pages.create.return_value = mock_page_response
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test\nContent")
            temp_path = f.name
        
        try:
            result = self.uploader.upload_markdown_file(
                filepath=temp_path,
                parent_url="https://notion.so/16132a3709e4816cb512e4d73d345003"
            )
            
            # Verify file was processed
            mock_processor.process_file.assert_called_once_with(temp_path)
            
            # Verify page was created
            self.mock_client.pages.create.assert_called_once()
            
            self.assertEqual(result, "new-page-id")
            
        finally:
            os.unlink(temp_path)

    @patch('notion_uploader.MarkdownProcessor')
    def test_upload_markdown_content_with_parent_url(self, mock_processor_class):
        """Test content upload using parent URL."""
        # Setup mocks  
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.parse_markdown_to_blocks.return_value = (
            [{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "test"}}]}}],
            "Test Title"
        )
        
        mock_page_response = {"id": "content-page-id"}
        self.mock_client.pages.create.return_value = mock_page_response
        
        result = self.uploader.upload_markdown_content(
            content="# Test\nContent",
            title="Test Content",
            parent_url="https://notion.so/16132a3709e4816cb512e4d73d345003"
        )
        
        # Verify content was processed
        mock_processor.parse_markdown_to_blocks.assert_called_once()
        
        # Verify page was created
        self.mock_client.pages.create.assert_called_once()
        
        self.assertEqual(result, "content-page-id")

    def test_upload_without_target_raises_error(self):
        """Test that missing target parameters raise ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test")
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                self.uploader.upload_markdown_file(filepath=temp_path)
            
            self.assertIn("Either parent_url, database_id or parent_page_id must be provided", 
                         str(context.exception))
        finally:
            os.unlink(temp_path)

    def test_list_database_pages(self):
        """Test database page listing."""
        mock_response = {
            "results": [
                {
                    "id": "page1", 
                    "properties": {
                        "title": {"title": [{"plain_text": "Page 1"}]}
                    }
                },
                {
                    "id": "page2",
                    "properties": {
                        "title": {"title": [{"plain_text": "Page 2"}]}
                    }
                }
            ]
        }
        self.mock_client.databases.query.return_value = mock_response
        
        result = self.uploader.list_database_pages("test-db-id", limit=10)
        
        self.mock_client.databases.query.assert_called_once_with(
            database_id="test-db-id",
            page_size=10
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "page1")

    def test_get_database_info(self):
        """Test database info retrieval."""
        mock_db_info = {
            "id": "test-db-id",
            "title": [{"plain_text": "Test Database"}],
            "created_time": "2025-01-01T00:00:00.000Z"
        }
        self.mock_client.databases.retrieve.return_value = mock_db_info
        
        result = self.uploader.get_database_info("test-db-id")
        
        self.mock_client.databases.retrieve.assert_called_once_with("test-db-id")
        self.assertEqual(result, mock_db_info)


if __name__ == '__main__':
    unittest.main()