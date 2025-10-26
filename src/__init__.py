"""
Markdown2Notion MCP Server Package

A FastMCP-based server for uploading Markdown files to Notion.
Uses filename as page title and supports various Markdown elements.
"""

__version__ = "0.1.0"
__author__ = "Markdown2Notion Team"

from .server import main
from .notion_uploader import NotionUploader
from .markdown_processor import MarkdownProcessor

__all__ = ["main", "NotionUploader", "MarkdownProcessor"]