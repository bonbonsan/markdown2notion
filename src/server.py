"""
Markdown2Notion MCP Server

FastMCP-based server for uploading Markdown files to Notion.
Uses filename as page title and supports database/parent page targets.
"""

import os
import sys
from typing import Optional
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastmcp import FastMCP

# Import handling for direct execution vs module import
if __name__ == "__main__":
    from notion_uploader import NotionUploader
else:
    from .notion_uploader import NotionUploader


# Initialize FastMCP server
mcp = FastMCP("Markdown2Notion")

# Global uploader instance
uploader = None


def get_uploader() -> NotionUploader:
    """Get or create NotionUploader instance."""
    global uploader
    if uploader is None:
        uploader = NotionUploader()
    return uploader


@mcp.tool()
def upload_markdown(
    filepath: str, 
    parent_url: Optional[str] = None,
    database_id: Optional[str] = None, 
    parent_page_id: Optional[str] = None
) -> str:
    """
    Upload a Markdown file to Notion as a new page.
    Uses the filename (without extension) as the page title.
    Automatically handles files with 100+ blocks.
    
    Args:
        filepath: Path to the Markdown file to upload
        parent_url: Notion page URL (e.g., https://notion.so/page-title-abc123...)
        database_id: Target Notion database ID (optional, alternative to parent_url)
        parent_page_id: Parent page ID (optional, alternative to parent_url)
        
    Returns:
        Success message with the created page ID
        
    Raises:
        Exception: If upload fails
    """
    try:
        uploader_instance = get_uploader()
        
        # Extract parent_page_id from URL if provided
        if parent_url:
            parent_page_id = uploader_instance.extract_page_id_from_url(parent_url)
        
        if not database_id and not parent_page_id:
            return "Error: Either parent_url, database_id, or parent_page_id must be provided"
        
        page_id = uploader_instance.upload_markdown_file(
            filepath=filepath,
            database_id=database_id,
            parent_page_id=parent_page_id
        )
        
        filename = Path(filepath).name
        clean_page_id = page_id.replace("-", "")
        page_url = f"https://www.notion.so/{clean_page_id}"
        
        return f"Successfully uploaded '{filename}' to Notion.\nPage ID: {page_id}\nView at: {page_url}"
        
    except FileNotFoundError:
        return f"Error: File not found: {filepath}"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error uploading markdown: {str(e)}"


@mcp.tool()
def upload_markdown_content(
    content: str,
    title: str,
    parent_url: Optional[str] = None,
    database_id: Optional[str] = None,
    parent_page_id: Optional[str] = None
) -> str:
    """
    Upload Markdown content directly to Notion as a new page.
    Automatically handles content with 100+ blocks.
    
    Args:
        content: Markdown content as string
        title: Page title to use
        parent_url: Notion page URL (e.g., https://notion.so/page-title-abc123...)
        database_id: Target Notion database ID (optional, alternative to parent_url)
        parent_page_id: Parent page ID (optional, alternative to parent_url)
        
    Returns:
        Success message with the created page ID
        
    Raises:
        Exception: If upload fails
    """
    try:
        uploader_instance = get_uploader()
        
        # Extract parent_page_id from URL if provided
        if parent_url:
            parent_page_id = uploader_instance.extract_page_id_from_url(parent_url)
        
        if not database_id and not parent_page_id:
            return "Error: Either parent_url, database_id, or parent_page_id must be provided"
        
        page_id = uploader_instance.upload_markdown_content(
            content=content,
            title=title,
            database_id=database_id,
            parent_page_id=parent_page_id
        )
        
        clean_page_id = page_id.replace("-", "")
        page_url = f"https://www.notion.so/{clean_page_id}"
        
        return f"Successfully uploaded content as '{title}' to Notion.\nPage ID: {page_id}\nView at: {page_url}"
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error uploading content: {str(e)}"


@mcp.tool()
def list_database_pages(database_id: str, limit: int = 10) -> str:
    """
    List pages in a Notion database (for debugging purposes).
    
    Args:
        database_id: The Notion database ID
        limit: Maximum number of pages to return (default: 10, max: 100)
        
    Returns:
        List of page titles and IDs
    """
    try:
        uploader_instance = get_uploader()
        pages = uploader_instance.list_database_pages(database_id, limit)
        
        if not pages:
            return f"No pages found in database {database_id}"
        
        result = f"Found {len(pages)} pages in database:\n"
        for page in pages:
            title_prop = page.get("properties", {}).get("title", {})
            if "title" in title_prop and title_prop["title"]:
                title = title_prop["title"][0].get("plain_text", "Untitled")
            else:
                title = "Untitled"
            result += f"- {title} (ID: {page['id']})\n"
        
        return result
        
    except Exception as e:
        return f"Error listing pages: {str(e)}"


@mcp.tool()
def get_database_info(database_id: str) -> str:
    """
    Get information about a Notion database.
    
    Args:
        database_id: The Notion database ID
        
    Returns:
        Database information
    """
    try:
        uploader_instance = get_uploader()
        db_info = uploader_instance.get_database_info(database_id)
        
        title_prop = db_info.get("title", [])
        title = ""
        if title_prop:
            title = title_prop[0].get("plain_text", "Untitled Database")
        
        return f"Database: {title}\nID: {database_id}\nCreated: {db_info.get('created_time', 'Unknown')}"
        
    except Exception as e:
        return f"Error getting database info: {str(e)}"


@mcp.prompt()
def markdown_upload_guide() -> str:
    """Guide for using the Markdown2Notion MCP server."""
    return """
# Markdown2Notion Usage Guide

This MCP server allows you to upload Markdown files to Notion. Here's how to use it:

## Available Tools

### upload_markdown
Upload a Markdown file to Notion:
- `filepath`: Path to your .md file
- `database_id`: Target database ID (optional)
- `parent_page_id`: Parent page ID (optional)

**Note**: The filename (without .md extension) will be used as the page title.

### upload_markdown_content
Upload Markdown content directly:
- `content`: Your markdown content as text
- `title`: Page title
- `database_id` or `parent_page_id`: Target location

### list_database_pages
List existing pages in a database for reference.

## Setup Requirements
1. Set NOTION_TOKEN environment variable
2. Ensure target database/page allows content creation
3. Use absolute file paths for best results

## Example Usage
```
upload_markdown("/path/to/my-document.md", database_id="your_db_id")
```
This creates a Notion page titled "my-document" with your markdown content.
"""


def main():
    """Main entry point for the server."""
    # Check for Notion token
    if not os.getenv("NOTION_TOKEN"):
        print("Warning: NOTION_TOKEN environment variable not set", file=sys.stderr)
    
    # Run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()