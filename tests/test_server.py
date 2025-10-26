"""Unit tests for MCP server functions."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile
import os
import json

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestMCPServer(unittest.TestCase):
    """Test cases for MCP server tools."""

    def setUp(self):
        """Set up test fixtures."""
        # Import server after path setup
        from server import upload_markdown, upload_markdown_content, get_uploader
        
        self.upload_markdown = upload_markdown
        self.upload_markdown_content = upload_markdown_content
        self.get_uploader = get_uploader

    @patch('server.get_uploader')
    def test_upload_markdown_success(self, mock_get_uploader):
        """Test successful markdown file upload."""
        # Setup mock uploader
        mock_uploader = Mock()
        mock_uploader.upload_markdown_file.return_value = "test-page-id-123"
        mock_get_uploader.return_value = mock_uploader
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test\nContent")
            temp_path = f.name
        
        try:
            result = self.upload_markdown(
                filepath=temp_path,
                parent_url="https://notion.so/test-page"
            )
            
            # Verify uploader was called correctly
            mock_uploader.upload_markdown_file.assert_called_once()
            call_args = mock_uploader.upload_markdown_file.call_args[1]
            
            self.assertEqual(call_args['filepath'], temp_path)
            self.assertIn('parent_page_id', call_args)
            
            # Verify response format
            self.assertIn("Successfully uploaded", result)
            self.assertIn("test-page-id-123", result)
            self.assertIn("https://www.notion.so/", result)
            
        finally:
            os.unlink(temp_path)

    @patch('server.get_uploader')
    def test_upload_markdown_file_not_found(self, mock_get_uploader):
        """Test handling of non-existent files."""
        mock_uploader = Mock()
        mock_uploader.upload_markdown_file.side_effect = FileNotFoundError("File not found")
        mock_get_uploader.return_value = mock_uploader
        
        result = self.upload_markdown(
            filepath="/nonexistent/file.md",
            parent_url="https://notion.so/test-page"
        )
        
        self.assertIn("Error: File not found", result)

    @patch('server.get_uploader')
    def test_upload_markdown_invalid_url(self, mock_get_uploader):
        """Test handling of invalid URLs."""
        mock_uploader = Mock()
        mock_uploader.extract_page_id_from_url.side_effect = ValueError("Invalid URL format")
        mock_get_uploader.return_value = mock_uploader
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test")
            temp_path = f.name
        
        try:
            result = self.upload_markdown(
                filepath=temp_path,
                parent_url="invalid-url"
            )
            
            self.assertIn("Error:", result)
            
        finally:
            os.unlink(temp_path)

    @patch('server.get_uploader')
    def test_upload_markdown_missing_target(self, mock_get_uploader):
        """Test handling of missing target parameters."""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test")
            temp_path = f.name
        
        try:
            result = self.upload_markdown(filepath=temp_path)
            
            self.assertIn("Error: Either parent_url, database_id, or parent_page_id must be provided", result)
            
        finally:
            os.unlink(temp_path)

    @patch('server.get_uploader')
    def test_upload_markdown_content_success(self, mock_get_uploader):
        """Test successful markdown content upload."""
        mock_uploader = Mock()
        mock_uploader.upload_markdown_content.return_value = "content-page-id-456"
        mock_get_uploader.return_value = mock_uploader
        
        result = self.upload_markdown_content(
            content="# Test Content\nSome text",
            title="Test Page",
            parent_url="https://notion.so/test-page"
        )
        
        # Verify uploader was called
        mock_uploader.upload_markdown_content.assert_called_once()
        
        # Verify response
        self.assertIn("Successfully uploaded content", result)
        self.assertIn("Test Page", result)
        self.assertIn("content-page-id-456", result)

    @patch('server.get_uploader')  
    def test_upload_markdown_content_missing_target(self, mock_get_uploader):
        """Test content upload with missing target."""
        result = self.upload_markdown_content(
            content="# Test",
            title="Test"
        )
        
        self.assertIn("Error: Either parent_url, database_id, or parent_page_id must be provided", result)

    def test_get_uploader_initialization(self):
        """Test uploader initialization and caching."""
        # Clear any existing global uploader
        import server
        server.uploader = None
        
        with patch.dict('os.environ', {'NOTION_TOKEN': 'test_token'}):
            with patch('server.NotionUploader') as mock_uploader_class:
                mock_instance = Mock()
                mock_uploader_class.return_value = mock_instance
                
                # First call should create new instance
                result1 = self.get_uploader()
                mock_uploader_class.assert_called_once()
                
                # Second call should return cached instance
                result2 = self.get_uploader()
                mock_uploader_class.assert_called_once()  # Still only called once
                
                self.assertEqual(result1, result2)

    @patch('server.get_uploader')
    def test_notion_api_error_handling(self, mock_get_uploader):
        """Test handling of Notion API errors."""
        mock_uploader = Mock()
        # Simulate a Notion API error
        mock_uploader.upload_markdown_file.side_effect = Exception("Notion API error: Rate limit exceeded")
        mock_get_uploader.return_value = mock_uploader
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test")
            temp_path = f.name
        
        try:
            result = self.upload_markdown(
                filepath=temp_path,
                parent_url="https://notion.so/test-page"
            )
            
            self.assertIn("Error uploading markdown:", result)
            self.assertIn("Notion API error", result)
            
        finally:
            os.unlink(temp_path)

    def test_url_to_page_id_extraction_integration(self):
        """Test URL extraction in server context."""
        from server import upload_markdown
        
        # This tests the integration of URL extraction in the server function
        # We'll mock the uploader but test that URL processing works correctly
        
        test_url = "https://www.notion.so/My-Page-16132a3709e4816cb512e4d73d345003"
        expected_id = "16132a37-09e4-816c-b512-e4d73d345003"
        
        with patch('server.get_uploader') as mock_get_uploader:
            mock_uploader = Mock()
            mock_uploader.extract_page_id_from_url.return_value = expected_id
            mock_uploader.upload_markdown_file.return_value = "test-page"
            mock_get_uploader.return_value = mock_uploader
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write("# Test")
                temp_path = f.name
            
            try:
                result = upload_markdown(
                    filepath=temp_path,
                    parent_url=test_url
                )
                
                # Verify URL extraction was called
                mock_uploader.extract_page_id_from_url.assert_called_once_with(test_url)
                
                # Verify upload was called with extracted ID
                call_args = mock_uploader.upload_markdown_file.call_args[1]
                self.assertEqual(call_args['parent_page_id'], expected_id)
                
            finally:
                os.unlink(temp_path)


class TestServerEnvironment(unittest.TestCase):
    """Test server environment and configuration."""
    
    def test_server_main_function_token_check(self):
        """Test main function token validation."""
        from server import main
        
        # Test with missing token
        with patch.dict('os.environ', {}, clear=True):
            with patch('sys.stderr') as mock_stderr:
                with patch('server.mcp.run') as mock_run:
                    main()
                    
                    # Should run despite warning
                    mock_run.assert_called_once_with(transport="stdio")

    def test_server_imports(self):
        """Test that all server imports work correctly."""
        try:
            from server import (
                upload_markdown,
                upload_markdown_content, 
                list_database_pages,
                get_database_info,
                markdown_upload_guide,
                main
            )
            
            # If we get here, imports worked
            self.assertTrue(True)
            
        except ImportError as e:
            self.fail(f"Server import failed: {e}")


if __name__ == '__main__':
    unittest.main()