"""
Notion API client module for uploading Markdown content to Notion.
Handles communication with Notion API and page creation.
"""

import os
from typing import List, Dict, Any, Optional
from notion_client import Client
from dotenv import load_dotenv

# Import handling for direct execution vs module import
try:
    from .markdown_processor import MarkdownProcessor
except ImportError:
    from markdown_processor import MarkdownProcessor


class NotionUploader:
    """
    Handles uploading Markdown content to Notion pages.
    Uses Notion API v1 for page creation and content management.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the NotionUploader.
        
        Args:
            token: Notion API token (if not provided, loads from environment)
        """
        # Load environment variables
        load_dotenv()
        
        self.token = token or os.getenv("NOTION_TOKEN")
        if not self.token:
            raise ValueError("NOTION_TOKEN is required. Set it as environment variable or pass as parameter.")
        
        self.client = Client(auth=self.token)
        self.processor = MarkdownProcessor()

    def upload_markdown_file(
        self, 
        filepath: str, 
        parent_url: Optional[str] = None,
        database_id: Optional[str] = None, 
        parent_page_id: Optional[str] = None
    ) -> str:
        """
        Upload a Markdown file to Notion as a new page.
        Automatically handles files with more than 100 blocks by splitting them.
        
        Args:
            filepath: Path to the Markdown file
            parent_url: Notion page URL (optional)
            database_id: Target database ID (optional)
            parent_page_id: Parent page ID (optional, used if database_id not provided)
            
        Returns:
            The ID of the created Notion page
            
        Raises:
            ValueError: If neither database_id nor parent_page_id is provided
            FileNotFoundError: If the file doesn't exist
        """
        # Extract parent_page_id from URL if provided
        if parent_url:
            parent_page_id = self.extract_page_id_from_url(parent_url)
        
        if not database_id and not parent_page_id:
            raise ValueError("Either parent_url, database_id or parent_page_id must be provided")
        
        # Process the Markdown file
        blocks, title = self.processor.process_file(filepath)
        
        # Create the page with blocks (handles 100+ block limitation automatically)
        return self._create_page_with_blocks(blocks, title, database_id, parent_page_id)

    def upload_markdown_content(
        self, 
        content: str, 
        title: str,
        parent_url: Optional[str] = None,
        database_id: Optional[str] = None, 
        parent_page_id: Optional[str] = None
    ) -> str:
        """
        Upload Markdown content directly to Notion as a new page.
        Automatically handles content with more than 100 blocks by splitting them.
        
        Args:
            content: Markdown content as string
            title: Page title
            parent_url: Notion page URL (optional)
            database_id: Target database ID (optional)
            parent_page_id: Parent page ID (optional, used if database_id not provided)
            
        Returns:
            The ID of the created Notion page
            
        Raises:
            ValueError: If neither database_id nor parent_page_id is provided
        """
        # Extract parent_page_id from URL if provided
        if parent_url:
            parent_page_id = self.extract_page_id_from_url(parent_url)
        
        if not database_id and not parent_page_id:
            raise ValueError("Either parent_url, database_id or parent_page_id must be provided")
        
        # Process the Markdown content
        blocks, _ = self.processor.parse_markdown_to_blocks(content, title)
        
        # Create the page with blocks (handles 100+ block limitation automatically)
        return self._create_page_with_blocks(blocks, title, database_id, parent_page_id)

    def get_database_info(self, database_id: str) -> Dict[str, Any]:
        """
        Get information about a Notion database.
        
        Args:
            database_id: The database ID
            
        Returns:
            Database information
        """
        return self.client.databases.retrieve(database_id)

    def get_page_info(self, page_id: str) -> Dict[str, Any]:
        """
        Get information about a Notion page.
        
        Args:
            page_id: The page ID
            
        Returns:
            Page information
        """
        return self.client.pages.retrieve(page_id)

    def list_database_pages(self, database_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List pages in a database.
        
        Args:
            database_id: The database ID
            limit: Maximum number of pages to return
            
        Returns:
            List of page information
        """
        response = self.client.databases.query(
            database_id=database_id,
            page_size=min(limit, 100)
        )
        return response["results"]

    def _create_page_with_blocks(
        self,
        blocks: List[Dict[str, Any]],
        title: str,
        database_id: Optional[str] = None,
        parent_page_id: Optional[str] = None
    ) -> str:
        """
        Create a Notion page with blocks, handling the 100-block limitation automatically.
        
        Args:
            blocks: List of Notion blocks to add to the page
            title: Page title
            database_id: Target database ID (optional)
            parent_page_id: Parent page ID (optional)
            
        Returns:
            The ID of the created Notion page
        """
        # Create page properties
        properties = {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        }
        
        # Determine the parent
        if database_id:
            parent = {"database_id": database_id}
        else:
            parent = {"page_id": parent_page_id}
        
        # Handle blocks based on count
        if len(blocks) <= 100:
            # Can create page with all blocks at once
            page = self.client.pages.create(
                parent=parent,
                properties=properties,
                children=blocks
            )
        else:
            # Create page with first 100 blocks
            initial_blocks = blocks[:100]
            page = self.client.pages.create(
                parent=parent,
                properties=properties,
                children=initial_blocks
            )
            
            # Add remaining blocks in chunks of 100
            page_id = page["id"]
            remaining_blocks = blocks[100:]
            
            # Process remaining blocks in chunks
            for i in range(0, len(remaining_blocks), 100):
                chunk = remaining_blocks[i:i+100]
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=chunk
                )
        
        return page["id"]

    @staticmethod
    def extract_page_id_from_url(url: str) -> str:
        """
        Extract page ID from a Notion URL.
        
        Args:
            url: Notion page URL (e.g., https://www.notion.so/16132a3709e4816cb512e4d73d345003)
            
        Returns:
            The extracted page ID
            
        Raises:
            ValueError: If URL is invalid or doesn't contain a page ID
        """
        import re
        
        # Remove any query parameters and fragments
        url = url.split('?')[0].split('#')[0]
        
        # Pattern to match Notion page URLs
        patterns = [
            # Standard format: https://notion.so/page-title-32chars
            r'notion\.so/[^/]*?([a-f0-9]{32})/?$',
            # Direct ID format: https://notion.so/32chars
            r'notion\.so/([a-f0-9]{32})/?$',
            # With subdomain: https://workspace.notion.site/page-title-32chars
            r'notion\.site/[^/]*?([a-f0-9]{32})/?$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                page_id = match.group(1)
                # Format as UUID with hyphens
                return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
        
        raise ValueError(f"Invalid Notion URL format: {url}")